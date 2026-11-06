"""Figuras analíticas próprias 16:9 para nacional e UFs, sem motor de vídeo."""
import argparse
import json
import math
import os
from pathlib import Path
import re

if __package__:
    from . import reconstruir_serie_temporal as temporal
    from .plotar_serie_temporal import segments, COLORS, LABELS
else:
    import reconstruir_serie_temporal as temporal
    from plotar_serie_temporal import segments, COLORS, LABELS

NAMES = {'br': 'Brasil', 'am': 'Amazonas', 'ba': 'Bahia', 'mg': 'Minas Gerais',
         'rj': 'Rio de Janeiro', 'sp': 'São Paulo', 'rs': 'Rio Grande do Sul'}
FOUR = ('ba', 'mg', 'sp', 'rj')
SIX = ('am', 'ba', 'mg', 'rj', 'sp', 'rs')
METRICS = ('quantidades', 'percentuais')


def select_areas(data, areas):
    """Ausência bloqueia: jamais substitui UF por outra nem cria uma linha zero."""
    result = {}
    for area in areas:
        if area not in data['series']:
            raise ValueError('Abrangência ausente: ' + area)
        rows = temporal.eligible_rows(data['series'][area])
        if not rows:
            raise ValueError('Sem observação elegível: ' + area)
        if any(row['area'] != area or row['capturePrecedesGeneration'] for row in rows):
            raise ValueError('Abrangência/cronologia inconsistente: ' + area)
        if rows != sorted(rows, key=lambda row: (row['generatedAt'], int(row['idg']))):
            raise ValueError('Série fora de ordem: ' + area)
        result[area] = rows
    return result


def quantity_ceiling(rows):
    """Escala absoluta em milhões, arredondada para cima sem recortar a curva."""
    highest = max(row['votes'][candidate] for row in rows for candidate in COLORS) / 1e6
    step = 10 if highest > 30 else 2 if highest > 10 else 1 if highest > 3 else 0.5
    return max(step, math.ceil(highest * 1.06 / step) * step)


def panel_specs(selected, areas, metric):
    if metric not in METRICS:
        raise ValueError('Métrica desconhecida')
    if metric == 'percentuais':
        minimum = min(row['shareValidPercent'][candidate] for area in areas
                      for row in selected[area] for candidate in COLORS
                      if row['shareValidPercent'][candidate] is not None)
        maximum = max(row['shareValidPercent'][candidate] for area in areas
                      for row in selected[area] for candidate in COLORS
                      if row['shareValidPercent'][candidate] is not None)
        # Mesma escala em todos os gráficos percentuais deste pacote; não corta dados.
        if minimum < 20 or maximum > 80:
            raise ValueError('Participação fora da escala comum declarada de20–80%')
        return {'metric': metric, 'yLimits': [20, 80], 'unit': '% dos votos válidos',
                'scale': 'common_20_80_percent'}
    common_top = max(quantity_ceiling(selected[area]) for area in areas)
    return {'metric': metric, 'yLimits': [0, common_top], 'unit': 'milhões de votos',
            'scale': 'common_absolute_within_figure' if len(areas) > 1 else 'absolute_local'}


def paint_figure(plt, dates, selected, areas, metric, threshold, png_path, svg_path):
    spec = panel_specs(selected, areas, metric)
    columns = 3 if len(areas) == 6 else 2 if len(areas) == 4 else 1
    rows_count = 2 if len(areas) > 1 else 1
    fig, axes = plt.subplots(rows_count, columns, figsize=(12.8, 7.2), squeeze=False)
    fig.subplots_adjust(left=0.065, right=0.98, top=0.77 if len(areas) > 1 else 0.78,
                         bottom=0.16, hspace=0.57, wspace=0.24)
    heading = 'Votos nominais divulgados' if metric == 'quantidades' else 'Participação nos votos válidos'
    scope = 'Brasil' if areas == ('br',) else '4 UFs' if len(areas) == 4 else '6 UFs' if len(areas) == 6 else NAMES[areas[0]]
    fig.suptitle(scope + ' • ' + heading, x=0.065, y=0.96, ha='left', fontsize=21, fontweight='bold')
    scale_label = ('Escala comum: 20%–80% dos votos válidos' if metric == 'percentuais'
                   else f"Escala {'comum' if len(areas) > 1 else 'absoluta'}: 0–{spec['yLimits'][1]:g} milhões de votos")
    fig.text(0.065, 0.905, '25/10/2026 • Brasília (UTC−03) • ' + scale_label, fontsize=12)
    fig.text(0.065, 0.858, '● Registros salvos. Cinza: lacunas > 5 min. Antes/depois da série: sem observação.',
             fontsize=10.5, color='#555555')
    legend_handles = []
    for area, ax in zip(areas, axes.flat):
        series = selected[area]
        for gap in temporal.gap_list(series, threshold):
            ax.axvspan(temporal.parse_instant(gap['from']), temporal.parse_instant(gap['to']),
                       color='#ededed', linewidth=0, zorder=0)
        for candidate, color in COLORS.items():
            for part in segments(series, threshold):
                x = [temporal.parse_instant(row['generatedAt']) for row in part]
                y = [row['votes'][candidate] / 1e6 if metric == 'quantidades'
                     else row['shareValidPercent'][candidate] for row in part]
                markers = sorted(set([0, len(part) - 1] + list(range(0, len(part), max(1, len(part) // 8)))))
                ax.plot(x, y, color=color, linewidth=2 if len(areas) == 1 else 1.7,
                        marker='o', markersize=3 if len(areas) == 1 else 2.2, markevery=markers)
            handle, = ax.plot([], [], color=color, linewidth=2, marker='o', markersize=4, label=LABELS[candidate])
            if area == areas[0]:
                legend_handles.append(handle)
        last = series[-1]
        pct = last['sections']['countedPercent']
        status = '100% das seções' if last['sections']['complete'] else f"{pct:.5f}% das seções • parcial".replace('.', ',')
        if len(areas) > 1:
            ax.set_title(area.upper() + ' — ' + NAMES[area], loc='left', fontsize=12, pad=30)
        ax.text(0, 1.045, 'Última ' + last['generatedAt'][11:19] + ' • ' + status,
                 transform=ax.transAxes, fontsize=8.7 if len(areas) > 1 else 11, color='#555555')
        ax.set_xlim(temporal.parse_instant('2026-10-25T16:50:00-03:00'),
                    temporal.parse_instant('2026-10-25T23:35:00-03:00'))
        ax.set_ylim(*spec['yLimits'])
        ax.xaxis.set_major_locator(dates.HourLocator(byhour=(17, 19, 21, 23), tz=temporal.BRASILIA))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M', tz=temporal.BRASILIA))
        ax.tick_params(labelsize=9 if len(areas) > 1 else 12)
        ax.grid(axis='y', color='#dddddd', linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_ylabel('milhões' if metric == 'quantidades' else '% dos válidos',
                       fontsize=9 if len(areas) > 1 else 12)
    fig.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(0.985, 0.905),
               ncol=2, frameon=False, fontsize=11, borderaxespad=0)
    fig.text(0.52, 0.097, 'Horário de Brasília • geração dos arquivos, não horário do voto', ha='center', fontsize=11)
    fig.text(0.065, 0.051, 'Fonte: TSE, cópias preservadas por Gabriel-Alexandre • cálculos e figuras próprios.',
             fontsize=8.5, color='#555555')
    fig.text(0.065, 0.027, 'Revisão ' + temporal.COMMIT + ' • linhas não preenchem as lacunas.',
             fontsize=8.2, color='#555555')
    metadata = {'Date': None, 'Creator': 'ALP / Matplotlib',
                'Description': f"{scope}: {heading}; {spec['unit']}; geração interpretada como Brasília; fontes atribuídas à revisão {temporal.COMMIT}."}
    with svg_path.open('w', encoding='utf-8', newline='\n') as output:
        fig.savefig(output, format='svg', metadata=metadata)
    # Remove somente espaços estruturais entre elementos, preservando texto e paths.
    compact_svg = re.sub(r'>\s+<', '><', svg_path.read_text(encoding='utf-8')).strip() + '\n'
    svg_path.write_text(compact_svg, encoding='utf-8', newline='\n')
    fig.savefig(png_path, format='png', dpi=100)
    plt.close(fig)
    return spec


def render_package(series_path, summary_path, output_dir, svg_dir):
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    expected = next(item['sha256'] for item in summary['derivativeArtifacts'] if item['name'] == series_path.name)
    if temporal.sha256(series_path) != expected:
        raise ValueError('Hash da série completa divergente')
    data = json.loads(series_path.read_text(encoding='utf-8'))
    if data['provenance'] != summary['provenance']:
        raise ValueError('Proveniência divergente')
    selected = select_areas(data, ('br',) + SIX)
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(output_dir / 'matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as dates
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
                                 'svg.hashsalt': 'alp-estados-temporal-v1',
                                 'axes.spines.top': False, 'axes.spines.right': False})
    groups = [('br', ('br',)), ('4ufs', FOUR), ('6ufs', SIX)] + [(area, (area,)) for area in SIX]
    assets = []
    threshold = summary['method']['gapAndStalenessThresholdSeconds']
    for group, areas in groups:
        for metric in METRICS:
            name = f'temporal-{group}-{metric}'
            svg_path, png_path = output_dir / (name + '.svg'), output_dir / (name + '.png')
            spec = paint_figure(plt, dates, selected, areas, metric, threshold, png_path, svg_path)
            svg_bytes = svg_path.read_bytes()
            if b'\r' in svg_bytes or len(svg_bytes) >= 100_000:
                raise ValueError('SVG fora do contrato LF/<100KB: ' + name)
            # Apenas as quatro grades vão ao diretório público; demais SVGs ficam nos dados.
            if len(areas) > 1:
                public_svg = svg_dir / svg_path.name
                if public_svg.resolve() != svg_path.resolve():
                    public_svg.write_bytes(svg_bytes)
            png_header = png_path.read_bytes()[:24]
            width = int.from_bytes(png_header[16:20], 'big')
            height = int.from_bytes(png_header[20:24], 'big')
            if (width, height) != (1280, 720):
                raise ValueError('PNG fora do contrato 1280x720')
            assets.append({'name': name, 'areas': list(areas), **spec,
                           'png': {'name': png_path.name, 'sha256': temporal.sha256(png_path),
                                   'bytes': png_path.stat().st_size, 'width': width, 'height': height},
                           'svg': {'name': svg_path.name, 'sha256': temporal.sha256(svg_path), 'bytes': len(svg_bytes)}})
    manifest = {'schema': 'alp.temporal-state-charts.v1', 'provenance': summary['provenance'],
                'sourceSeriesSha256': expected, 'sourceSummarySha256': temporal.sha256(summary_path),
                'matplotlibVersion': matplotlib.__version__, 'timeAxis': 'generation interpreted as America/Sao_Paulo UTC-03',
                'gapThresholdSeconds': threshold, 'assets': assets,
                'areas': {area: {'records': len(rows), 'firstGenerationAt': rows[0]['generatedAt'],
                                 'lastGenerationAt': rows[-1]['generatedAt'], 'lastSections': rows[-1]['sections'],
                                 'gaps': temporal.gap_list(rows, threshold)} for area, rows in selected.items()}}
    temporal.write_json(output_dir / 'manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--series', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--svg-dir', type=Path, required=True)
    args = parser.parse_args()
    manifest = render_package(args.series, args.summary, args.output_dir, args.svg_dir)
    print(json.dumps({'assets': len(manifest['assets']), 'pngSize': [1280, 720],
                      'manifestSha256': temporal.sha256(args.output_dir / 'manifest.json')}, indent=2))


if __name__ == '__main__':
    main()
