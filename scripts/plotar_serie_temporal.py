"""Plota derivados verificados; Matplotlib é opcional e não é instalado aqui."""
import argparse
from datetime import timedelta
import json
import os
from pathlib import Path

if __package__:
    from . import reconstruir_serie_temporal as temporal
else:
    import reconstruir_serie_temporal as temporal

COLORS = {'lula': '#176e91', 'flavio': '#d47428'}
LABELS = {'lula': 'Lula', 'flavio': 'Flávio'}


def segments(rows, threshold):
    """Nunca liga a linha através de um intervalo maior que o limiar."""
    output = []
    for row in rows:
        if not output or (temporal.parse_instant(row['generatedAt']) - temporal.parse_instant(output[-1][-1]['generatedAt'])).total_seconds() > threshold:
            output.append([])
        output[-1].append(row)
    return output


def rate_windows(rows, threshold):
    """Janelas de 30 min; incremento asof dividido pelo tamanho fixo da janela."""
    output = []
    start = temporal.parse_instant('2026-10-25T17:00:00-03:00')
    limit = temporal.parse_instant('2026-10-25T23:30:00-03:00')
    while start < limit:
        end = start + timedelta(minutes=30)
        a, b = temporal.asof(rows, start), temporal.asof(rows, end)
        status = temporal.window_rate(a, b, rows, threshold)
        stale = any(point is not None and (target - temporal.parse_instant(point['generatedAt'])).total_seconds() > threshold
                    for point, target in ((a, start), (b, end)))
        usable = status['status'] == 'observed_endpoints' and not status['notContinuous'] and not stale
        output.append({'from': start.isoformat(), 'to': end.isoformat(),
                       'sourceFromIdg': a['idg'] if a else None, 'sourceToIdg': b['idg'] if b else None,
                       'usable': usable, 'status': status['status'],
                       'containsGap': status['notContinuous'], 'staleEndpoint': stale,
                       'votesPerMinute': {candidate: (b['votes'][candidate] - a['votes'][candidate]) / 30
                                          for candidate in COLORS} if usable else None})
        start = end
    return output


def render(series_path, summary_path, svg_path, png_path):
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    expected = next(artifact['sha256'] for artifact in summary['derivativeArtifacts']
                    if artifact['name'] == series_path.name)
    if temporal.sha256(series_path) != expected:
        raise ValueError('Série completa diverge do hash registrado no resumo')
    data = json.loads(series_path.read_text(encoding='utf-8'))
    if data['provenance'] != summary['provenance']:
        raise ValueError('Proveniência da série diverge do resumo')
    rows = temporal.eligible_rows(data['series']['br'])
    threshold = summary['method']['gapAndStalenessThresholdSeconds']
    gaps = temporal.gap_list(rows, threshold)
    windows = rate_windows(rows, threshold)
    if any(row['area'] != 'br' or row['capturePrecedesGeneration'] for row in rows):
        raise ValueError('O gráfico exige nacional com cronologia de captura consistente')
    if any(rate < 0 for window in windows if window['usable'] for rate in window['votesPerMinute'].values()):
        raise ValueError('Queda nominal exige revisão antes de plotar este perfil')

    png_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(png_path.parent / 'matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as dates
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter, MultipleLocator
    matplotlib.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                                 'svg.fonttype': 'none', 'svg.hashsalt': 'alp-temporal-v1',
                                 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(3, 1, figsize=(11, 8.2), sharex=True,
                             gridspec_kw={'height_ratios': (2.2, 1.6, 1.6)})
    fig.subplots_adjust(left=0.09, right=0.98, top=0.87, bottom=0.14, hspace=0.23)
    fig.suptitle('Como os totais divulgados evoluíram em 25/10/2026', x=0.09, y=0.965,
                 ha='left', fontsize=16, fontweight='bold')
    fig.text(0.09, 0.925, 'Brasil • 346 versões nacionais preservadas • geração do JSON em Brasília (UTC−03)', fontsize=10)
    fig.text(0.09, 0.898, '● Registros salvos; linhas guiam a leitura. Geração não é horário do voto nem prova de disponibilidade pública.',
             fontsize=8, color='#505050')
    for ax in axes:
        for gap in gaps:
            ax.axvspan(temporal.parse_instant(gap['from']), temporal.parse_instant(gap['to']),
                       facecolor='#eeeeee', edgecolor='none', zorder=0)
        ax.grid(axis='y', color='#dddddd', linewidth=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', labelsize=8)
        ax.set_xlim(temporal.parse_instant('2026-10-25T16:45:00-03:00'),
                    temporal.parse_instant('2026-10-25T23:35:00-03:00'))
    for candidate, color in COLORS.items():
        for part in segments(rows, threshold):
            x = [temporal.parse_instant(row['generatedAt']) for row in part]
            marker_indices = sorted(set([0, len(part) - 1] + list(range(0, len(part), 25))))
            axes[0].plot(x, [row['votes'][candidate] / 1e6 for row in part], color=color,
                         linewidth=1.6, marker='o', markersize=2.4, markevery=marker_indices)
            axes[2].plot(x, [row['shareValidPercent'][candidate] for row in part], color=color,
                         linewidth=1.5, marker='o', markersize=2.4, markevery=marker_indices)
        axes[0].plot([], [], color=color, marker='o', markersize=3, label=LABELS[candidate])
        for window in windows:
            if not window['usable']:
                continue
            center = temporal.parse_instant(window['from']) + timedelta(minutes=15)
            offset = timedelta(minutes=-4 if candidate == 'lula' else 4)
            axes[1].bar(center + offset, window['votesPerMinute'][candidate] / 1000,
                        width=7 / (24 * 60), color=color, edgecolor='none', zorder=3)
    axes[0].set_ylim(0, 72)
    axes[0].set_ylabel('Votos nominais\n(milhões)')
    axes[0].legend(loc='lower right', frameon=False, ncol=2, fontsize=9)
    axes[0].text(temporal.parse_instant('2026-10-25T18:04:00-03:00'), 59,
                 'Sem capturas nacionais\n17:07:01 → 19:01:56', ha='center', fontsize=8, color='#666666')
    axes[0].text(temporal.parse_instant('2026-10-25T22:54:00-03:00'), 56,
                 'Sem capturas\n22:22:01 → 23:27:02', ha='center', fontsize=7.4, color='#666666')
    axes[0].annotate('Primeiro registro: 17:06:31\nAntes disso: sem observação',
                     xy=(temporal.parse_instant(rows[0]['generatedAt']), 0.19),
                     xytext=(temporal.parse_instant('2026-10-25T18:00:00-03:00'), 22),
                     fontsize=7.5, ha='center', color='#444444',
                     arrowprops={'arrowstyle': '-', 'color': '#888888', 'linewidth': 0.7})
    axes[1].set_ylabel('Incremento médio\n(mil votos/min)')
    axes[1].set_ylim(0, 820)
    axes[1].yaxis.set_major_locator(MultipleLocator(200))
    axes[1].text(0.01, 0.92, 'Janelas fixas de 30 min: Δ entre versões asof dos limites ÷ 30.',
                 transform=axes[1].transAxes, fontsize=7.5, color='#444444')
    axes[1].text(0.01, 0.81, 'Sem barra = limite ausente/antigo ou lacuna; não significa zero.',
                 transform=axes[1].transAxes, fontsize=7.5, color='#444444')
    last = [window for window in windows if window['usable']][-1]
    if max(last['votesPerMinute'].values()) < 10_000:
        small_label = ('21:30–22:00\nLula / Flávio: ' +
                       ' / '.join(f"{last['votesPerMinute'][candidate] / 1000:.2f}".replace('.', ',')
                                  for candidate in COLORS) + ' mil/min')
        axes[1].annotate(small_label, xy=(temporal.parse_instant(last['from']) + timedelta(minutes=15), 3),
                         xytext=(temporal.parse_instant(last['to']), 110), fontsize=7.3, ha='center',
                         color='#555555', arrowprops={'arrowstyle': '-', 'color': '#999999', 'linewidth': 0.6})
    axes[2].set_ylabel('Participação nos\nvotos válidos (%)')
    axes[2].set_ylim(40, 60)
    axes[2].yaxis.set_major_locator(MultipleLocator(5))
    axes[2].yaxis.set_major_formatter(FuncFormatter(lambda value, position: str(int(value))))
    axes[2].set_xlabel('Horário de Brasília em 25/10/2026 • sem interpolação nas faixas cinzas', labelpad=9)
    axes[2].xaxis.set_major_locator(dates.HourLocator(tz=temporal.BRASILIA))
    axes[2].xaxis.set_major_formatter(dates.DateFormatter('%H:%M', tz=temporal.BRASILIA))
    fig.text(0.09, 0.055, 'Fonte: JSONs TSE preservados por Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026.',
             fontsize=7.5, color='#555555')
    fig.text(0.09, 0.033, 'Revisão ' + temporal.COMMIT + ' • código e cálculos próprios; aquisição original não repetida.',
             fontsize=7.5, color='#555555')
    with svg_path.open('w', encoding='utf-8', newline='\n') as svg_stream:
        fig.savefig(svg_stream, format='svg', metadata={'Date': None, 'Creator': 'ALP / Matplotlib',
                                                       'Description': 'Curva de versões nacionais preservadas, com lacunas explícitas e taxas asof em janelas de30min.'})
    fig.savefig(png_path, format='png', dpi=150)
    plt.close(fig)
    if svg_path.stat().st_size >= 100_000:
        raise ValueError('SVG excede o limite solicitado de100KB')
    manifest = {'schema': 'alp.temporal-plot.v1', 'sourceSummarySha256': temporal.sha256(summary_path),
                'sourceSeriesSha256': expected, 'matplotlibVersion': matplotlib.__version__,
                'nationalVersions': len(rows), 'gaps': gaps, 'windows': windows,
                'svgSha256': temporal.sha256(svg_path), 'svgBytes': svg_path.stat().st_size,
                'pngSha256': temporal.sha256(png_path)}
    temporal.write_json(png_path.parent / 'plot-manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--series', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--svg', type=Path, required=True)
    parser.add_argument('--png', type=Path, required=True)
    args = parser.parse_args()
    manifest = render(args.series, args.summary, args.svg, args.png)
    print(json.dumps({'svgBytes': manifest['svgBytes'], 'svgSha256': manifest['svgSha256'],
                      'usableRateWindows': sum(window['usable'] for window in manifest['windows'])}, indent=2))


if __name__ == '__main__':
    main()
