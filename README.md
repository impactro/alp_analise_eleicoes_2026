# ALP — análise das eleições de 2026

**Revisão ampliada de05/11/2026: oito blocos numéricos reproduzidos em fontes
primárias, cinco recalculados nas bases preservadas pelo autor. A investigação
causal das24 hipóteses não está concluída.**

Projeto de Fábio Souza / CrânIA para conferir números eleitorais com fontes
abertas, Python e método explícito. Cada leitor deve poder encontrar a origem,
refazer a conta e apontar uma divergência. A conclusão não é escolhida antes
da execução.

O ponto de partida é o vídeo [Eleitores mortos votaram no 2º turno?](https://www.youtube.com/watch?v=l5aT6mD0Hpo),
de Gabriel Carvalho, publicado em 30/10/2026. Seu
[projeto original](https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026)
é referência e objeto de replicação, não resultado independente deste repositório.
Revisão de referência: `4a12ed014cf7927df24226f900450db7fe5b1a22`.

## O que já existe

- [Linha do tempo de divulgação](docs/linha-do-tempo-divulgacao.md): 16 quadros
  com relógio de CNN/Band conferidos, 346 versões nacionais, taxas por intervalo
  e decomposição regional. [Gráfico](docs/figuras/curva-divulgacao.svg),
  [observações e localizadores](fontes/observacoes-divulgacao.json) e
  [confronto reproduzido](resultados/confronto-divulgacao.json). Esta rodada
  amplia H17/H24 sem concluir o efeito causal da prorrogação.
- [Gráficos de quatro e seis estados](docs/reproduzir-graficos-uf.md),
  [fontes oficiais de histórico e documentos](fontes/fontes-temporais-oficiais.json)
  e [roteiro da prévia R6](docs/roteiro-episodio-r6-previa.md).
  [Laudo da rodada temporal](resultados/revisao_temporal.json): 21 confrontos
  nacionais coincidem; uma leitura estadual segue sem correspondência na
  coleção preservada. Isso não representa uma porcentagem de verdade do vídeo.
- [Revisão ampliada e correção de contexto](docs/revisao-ampliada.md): o original
  testa hipóteses do público; não apresenta24 afirmações factuais do autor.
- [Idade e comparecimento](resultados/idade.json), [histórico2018/2022/2026](resultados/historico_secoes.json)
  e [municípios/estados/abstenção/ganho líquido](resultados/municipios.json),
  com programas próprios e hashes de fontes primárias.
- [Recálculos das bases/capturas preservadas](resultados/capturas.json),
  separados da reconstrução primária e da conferência aritmética isolada.
- [Roteiro R5 revisado](docs/roteiro-episodio-r5.md) e [matriz atualizada das24 hipóteses](analise/grade-validacao-r5.json).
- [Como reproduzir a ampliação](docs/reproduzir-revisao-ampliada.md) e
  [pacote para integração futura no Pergunte Aí](docs/pergunte-ai-handoff.md).

As entradas abaixo preservam a construção e a primeira rodada:

- [Proposta editorial e escopo](docs/proposta.md) de um vídeo extra da CrânIA,
  fora da agenda regular.
- [Matriz das 24 alegações](analise/alegacoes.json), com timestamps e situação.
- [Fontes e versões](fontes/manifesto.json).
- [Método e critérios de validação](docs/metodo.md).
- [Primeiro controle dos totais](resultados/controle_nacional.json), calculado
  diretamente do ZIP oficial, sem depender do código ou banco do autor do vídeo.
- [Contagem de seções sem voto para Flávio](resultados/secoes_zero_voto.json):
  106 seções, 14.860 votos para Lula e 29 sem brancos/nulos, no recorte documentado.
  [Programa e instruções de reprodução](docs/reproduzir-secoes.md).
- [Resultado e limites da primeira rodada](docs/validacao-primeira-rodada.md):
  H01 (horários) e H13 (idade/comparecimento) permanecem pendentes.
- [Roteiro do episódio](docs/roteiro-episodio.md), com as pendências explicitadas
  no vídeo produzido.
- [Proposta original do roteiro](docs/roteiro-preliminar.md), preservada como histórico.
- [Prompt público de reprodução](docs/prompt-reproducao.md), apresentado no
  encerramento junto do endereço do GitHub.

## Vídeo anterior à revisão ampliada

A R4 abaixo registra a primeira reprodução e a direção visual. A revisão
ampliada posterior está no roteiro R5; ainda não há vídeo R5 neste registro.

[Assista à versão R4 com narração e trilha](https://www.youtube.com/watch?v=BjdS7e6yZ3k),
disponível como **não listada**: **5min08s, Full HD**.
O [roteiro R4](docs/roteiro-episodio-r4.md) abre com os 24 itens, apresenta o
status de cada proposição e indica o que falta para conferir.
O [mapa de apresentação](analise/grade-validacao-r4.json) distingue as contagens
de 2026 confirmadas das parcelas ainda pendentes.
O prompt completo, os programas e as fontes estão na descrição do vídeo e
neste repositório. Agradecimento ao estudo original no encerramento.
[Evidência do arquivo e da publicação R4](resultados/video-r4.json):
processamento concluído, capa aplicada e QA de plataforma aprovado em 05/11/2026.

As versões anteriores continuam disponíveis para comparação:

[Assista ao vídeo no YouTube](https://www.youtube.com/watch?v=fOl4hBpaMp0),
disponível como **não listado**: **6min28s, Full HD**, com lousas, Traço
Robótico, prompt/GitHub e agradecimento ao estudo original. Processamento
concluído em 04/11/2026; capa aplicada.
[Evidência pequena do arquivo, escopo e hashes](resultados/video.json).
O vídeo e os arquivos brutos ficam fora deste Git.

A [prévia visual R4, sem áudio](https://www.youtube.com/watch?v=TU1AyhsBvWE)
está disponível como **não listada** para avaliar no YouTube.
[Evidência da prévia e seus limites](resultados/video-r4-previa-visual.json).
A R4 com narração é o link principal acima.

## Reproduzir o primeiro controle

Requisito: Python 3.12 ou posterior; não há pacotes externos.

1. Baixe o arquivo indicado em `fontes/manifesto.json`, no conjunto
   [Resultados 2026 do TSE](https://dadosabertos.tse.jus.br/dataset/resultados-2026).
   Guarde-o em `local/brutos/`, que é ignorado pelo Git.
2. Execute na raiz:

```text
python -s scripts/conferir_totais.py --zip local/brutos/votacao_candidato_munzona_2026.zip --sha256 6d60a212fc46541fbf605da38ad1fcdd83deda030b802e70405ba6b9a01289c1
python -s -m unittest discover -s tests -v
```

O comando emite JSON para stdout. Para guardar uma execução, use redirecionamento
para `local/controle_nacional.json`. Não sobrescreva um resultado revisado sem
conferir o diff. Não extrai o ZIP, não faz rede, não chama modelos e não altera
o arquivo de origem. Lê somente o membro nacional presidencial `_BR.csv`,
separa Brasil/exterior e não soma o arquivo `BRASIL.csv` duplicado.

O SHA-256 fixa a edição usada no primeiro controle. Se a fonte oficial mudar,
o comando falha ao comparar hashes: uma nova edição deve ter novo manifesto,
nova execução e comparação explícita. Não estamos redistribuindo a cópia antiga;
se ela deixar de estar disponível, a reprodução exata dependerá de uma cópia
preservada pelo leitor. Versão atual e versão histórica não são intercambiáveis.

## Repositório pequeno, evidência aberta

Entram no Git: programas próprios, documentação, URLs, licenças das fontes,
hashes, pequenas tabelas agregadas em JSON e evidências revisadas.

Dados brutos públicos continuam nas fontes; cópias de trabalho ficam fora do Git.
Vídeos, transcrições integrais e relatórios de terceiros não são republicados.
Resultados municipais ou por seção só serão adicionados no tamanho e recorte
necessários, com metodologia, sem dados pessoais.

O controle nacional e H07 usam edições diferentes, identificadas nos resultados;
não combinar seus universos silenciosamente. A reprodução das contagens não
audita individualmente eleitores nem certifica integridade do sistema eleitoral.
Os novos resultados e os limites atuais estão na revisão ampliada; a primeira
rodada e os vídeos anteriores não são sobrescritos como se já os incluíssem.

## Relação com ALP e os vídeos

O Pergunte Aí é um ambiente de estudo e consulta a dados; a evidência deste
projeto continua disponível sem ele. Para experimentar:
[Pergunte Aí](https://conhecimento.crania.ia.br/pergunteai).
O vídeo pretende demonstrar IA aplicada com contexto, execução e supervisão
humana, incluindo lousa progressiva e desenhos que expliquem as contas.

Novos dados úteis poderão ser propostos ao ALP depois de conferir procedência,
licença, cobertura, atualização e testes. Este projeto não atualiza o agente
web ou WhatsApp automaticamente.

Código e textos originais deste projeto: licença MIT. Fontes externas mantêm
suas próprias condições; abertura de um repositório não licencia automaticamente
conteúdo de terceiros.
