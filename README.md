# ALP — análise das eleições de 2026

**Estado: primeira rodada independente com controle nacional e H07 reproduzidos. A investigação das
24 alegações não está concluída.**

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

## Vídeo desta rodada

[Assista ao vídeo no YouTube](https://www.youtube.com/watch?v=fOl4hBpaMp0),
disponível como **não listado**: **6min28s, Full HD**, com lousas, Traço
Robótico, prompt/GitHub e agradecimento ao estudo original. Processamento
concluído em 04/11/2026; capa aplicada.
[Evidência pequena do arquivo, escopo e hashes](resultados/video.json).
O vídeo e os arquivos brutos ficam fora deste Git.

Uma revisão está em produção: [roteiro R4](docs/roteiro-episodio-r4.md), com
os 24 itens na abertura, status por proposição e o caminho para verificar.
O [mapa de apresentação](analise/grade-validacao-r4.json) separa as contagens
de 2026 confirmadas das parcelas ainda pendentes. O link acima continua
identificando a versão já enviada; ainda não há publicação da revisão R4.

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
Os demais números permanecem em validação.

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
