# Figuras analíticas nacionais e por UF

O [gerador separado](../scripts/plotar_estados_temporal.py) produz figuras
próprias para revisão visual, sem modificar o gráfico nacional original ou
usar um motor de vídeo. Exige Python 3.12 e Matplotlib já instalado; não
instala dependências. Entradas são o resumo e a série completa verificados
pelos hashes descritos em [reproduzir a série](reproduzir-serie-temporal.md).

```text
python -s scripts/plotar_estados_temporal.py --series local/derivados/linha-tempo/series-completas.json --summary resultados/serie_temporal.json --output-dir local/figuras-temporais --svg-dir docs/figuras
python -s -m unittest tests.test_plotar_estados_temporal -v
```

O pacote contém 18 PNGs de 1280×720 e os SVGs equivalentes:

- nacional, quantidades e percentuais;
- grade 2×2 de BA, MG, SP e RJ, quantidades e percentuais;
- grade 2×3 de AM, BA, MG, RJ, SP e RS, quantidades e percentuais;
- seis UFs individuais, cada uma em quantidades e percentuais.

Os nomes seguem `temporal-<br|4ufs|6ufs|uf>-<quantidades|percentuais>`.
PNG, SVG e `manifest.json` ficam no destino declarado por `--output-dir`.
Somente as quatro grades próprias em SVG, cada uma abaixo de 100 KB, são
copiadas também para `--svg-dir`, mantendo o Git pequeno. Os nacionais e
individuais ficam somente no diretório de dados, com seus hashes no manifesto.
Os dados brutos não entram no Git. JSONs e SVGs próprios
usam UTF-8/LF explícito, sem normalizar nenhuma fonte bruta.

Quantidades e percentuais são figuras diferentes. As grades de quantidades
compartilham escala absoluta de 0 a 16 milhões; não normalizam a contagem de
cada UF. O nacional usa 0 a 70 milhões. Nos individuais, o limite superior
é calculado para a UF e declarado no cabeçalho: não comparar a inclinação
visual de gráficos com escalas verticais distintas como se fosse uma taxa.

Todos os percentuais usam a mesma escala de 20% a 80% dos votos válidos,
declarada no cabeçalho. O programa bloqueia se algum ponto sair desse
intervalo, em vez de cortar a curva. Todos os gráficos usam o mesmo eixo
horário de 16h50 a 23h35, interpretando geração como Brasília UTC−03 em
25/10/2026. Geração não é horário do voto nem prova de disponibilidade pública.

O gráfico preserva cada versão elegível da própria UF. Não soma UFs como
um nacional síncrono. Intervalos maiores que cinco minutos interrompem as
linhas e recebem fundo cinza; pontos isolados continuam visíveis. Antes
da primeira versão e após a última, não se desenha curva nem zero. Datas
anteriores ou registros de inicialização são excluídos das figuras analíticas.
UF ausente, sem observação elegível ou com cronologia contraditória bloqueia
a geração, sem substituição por outra série.

Cada painel mostra o horário da última versão e o percentual de seções
efetivamente preservado. AM, BA e MG continuam explicitamente parciais;
RJ, SP e RS têm 100% das seções em suas últimas versões salvas. A palavra
"parcial" não é removida por arredondamento para 100%.

O manifesto guarda hashes do resumo, da série completa, dos PNGs e dos SVGs,
dimensões, unidades, limites verticais, abrangências, primeira/última geração,
última cobertura e todas as lacunas por UF. Os testes verificam ausência de
UF, exclusão da inicialização, gaps com pontos isolados, cronologia, escala
absoluta comum e proteção contra corte do percentual.
