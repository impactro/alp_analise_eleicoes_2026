# Primeira rodada independente — 4 de novembro de 2026

| Item | Resultado próprio | Situação para narração |
| --- | --- | --- |
| H07: seções sem voto para Flávio | 106; 14.860 votos para Lula; 29 sem brancos/nulos; 15.222 comparecimentos | Reproduzido diretamente dos ZIPs oficiais no recorte definido |
| H01: 52,39% e ajuste de fuso | Sem resultado próprio | Pendente de BWeb com abertura/encerramento e tratamento documentado dos fusos |
| H13: 297.977 eleitores 100+, 149.424 residentes 96+, 2.141 comparecimentos | Sem reprodução independente desses três insumos | Números da referência, ainda pendentes de conferência nas fontes primárias |

H07 foi implementada de forma independente com biblioteca padrão e executada
sobre dois arquivos TSE previamente disponíveis. Fontes, hashes, gerações e
recorte estão em `resultados/secoes_zero_voto.json`; o procedimento está em
`docs/reproduzir-secoes.md`. A execução final dos ZIPs levou 64,861 segundos nesta
máquina. Os doze testes da suíte passaram. Uma consulta SQL própria, de leitura,
à base local produziu os mesmos quatro agregados antes da leitura dos ZIPs;
a execução pública não depende desse banco. As duas vias usam a mesma fonte
TSE, portanto não representam confirmação por duas autoridades independentes.

O controle nacional já registrado em `resultados/controle_nacional.json`
usa uma edição posterior da base municipal. Não juntar silenciosamente
os totais nacionais dessa edição com os microdados por seção de 26/10.
O exterior também é um universo diferente do recorte doméstico de H07.

Para H01, o detalhe disponível contém recebimento do boletim e primeira
totalização. Esses carimbos não substituem a hora de encerramento da votação.
Não se pode usar esse arquivo para dizer que os percentuais 52,39% e 50,99%
foram reproduzidos. O relatório de Gabriel Carvalho apresenta esses percentuais;
esta rodada ainda não os recalculou. A próxima execução precisa do recurso
oficial BWeb identificado, hash, chave de seção, abertura/encerramento,
votação, exclusões, limiar exato (17h00 versus 17h00min59) e conversão de horário.
O relatório de referência e seu JSON contêm revisões de contagens de votos
tardios; não combinar números de versões diferentes para preencher a lacuna.

Para H13, foram identificados os recursos oficiais de perfil e comparecimento.
O HEAD do perfil respondeu 200 e informou 408.490.728 bytes. Não houve obtenção
de conteúdo validado: a tentativa da API IBGE terminou em timeout; a do ZIP de
comparecimento terminou em falha de DNS. A consulta pela API no navegador
interno também terminou em timeout; a abertura da tabela SIDRA falhou em DNS. Nenhum hash de conteúdo pode ser
atribuído a essas fontes nesta rodada. A disponibilidade dos dois turnos
também precisa ser conferida no arquivo efetivamente baixado.

A conta `297977 - 149424 = 148553` é aritmeticamente correta, mas essa
subtração não valida os insumos nem identifica pessoas falecidas. População
residente do Censo e cadastro eleitoral têm datas, cobertura e conceitos
distintos. A taxa `2141 / 297977 * 100` é aproximadamente 0,72%, condicionada
a esses números ainda não reproduzidos e à compatibilidade dos denominadores.
Não usar a diferença agregada como contagem de óbitos nem saldo eleitoral
como rastreamento de transferência individual de voto.

As demais hipóteses permanecem pendentes. A reprodução de H07 dá um bloco
verificável ao vídeo; H01/H13 devem aparecer como limites da presente checagem
ou aguardar a execução complementar. O prompt público deve pedir os resultados
de cada execução, sem exigir que o programa alcance os números da referência.

Executor desta fatia: DEV-python; execução própria e testes próprios, sem
aprovação QA independente. Engine de cálculo: Python stdlib em CPU; GPU não
se aplica ao parsing CSV/ZIP. Tokens oficiais e custo oficial não expostos:
`null`. Nenhuma mídia, fonte ativa, configuração do ALP ou publicação foi alterada.
