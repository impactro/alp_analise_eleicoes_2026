# Revisão ampliada — 5 de novembro de 2026

A revisão anterior explorou pouco o projeto original e apresentou pendências
da nossa execução de uma forma que diminuía o número de contas verificáveis.
O repositório do autor já estava referenciado; faltava usá-lo melhor para
encontrar fontes, fórmulas, versões e testes. Esta rodada corrige isso.

## O contexto original

A descrição pública do [vídeo de Gabriel Carvalho](https://www.youtube.com/watch?v=l5aT6mD0Hpo)
foi lida novamente, junto da transcrição preservada, do relatório, dos scripts,
dos manifestos e dos resultados. Ela aponta diretamente para o
[projeto completo](https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026),
o resumo, as 24 hipóteses, a revisão adversarial e os dois vídeos anteriores.
A revisão fixada é `4a12ed014cf7927df24226f900450db7fe5b1a22`, ainda o HEAD
consultado nesta rodada. Os outros projetos da série são
[pesquisas e resultado](https://github.com/Gabriel-Alexandre/pesquisas-e-resultado-segundo-turno-2026)
e [investigação das urnas](https://github.com/Gabriel-Alexandre/investigacao-segundo-turno-2026).

O autor testa **hipóteses de terceiros**, incluindo comentários do público e um
relatório que circulou nas redes. Não afirma que as 24 hipóteses são fatos.
Seu relatório informa 22 testadas: 8 desmentidas, 10 não sustentadas e
4 compatíveis com as duas interpretações; 2 não testadas. Esses são os
vereditos **dele sobre as hipóteses**, não o resultado automático desta revisão.

A frase «não reproduzimos ainda» informa o estado do nosso trabalho. Ela
não significa que a fonte não existe, que o cálculo está errado ou que a
hipótese é impossível de testar.

## Novos resultados em fontes primárias

Os programas abaixo são implementações próprias. Não executamos os scripts do
autor nem importamos seus bancos para obter os resultados desta tabela.

| Conta delimitada | Resultado desta rodada | Evidência |
|---|---|---|
| Cadastro brasileiro de eleitores 100+ em 2026 | **297.977** | [Idade](../resultados/idade.json) |
| População residente de 96+ no Censo2022 | **149.424** | [Idade](../resultados/idade.json) |
| Diferença entre esses dois totais | **148.553** | [Idade](../resultados/idade.json) |
| Comparecimento100+ no primeiro turno | **2.141**, taxa **0,718512%**, arredondada **0,72%** | [Idade](../resultados/idade.json) |
| Seções sem voto para Bolsonaro em 2018/2022 | **328 / 141**, Brasil sem exterior | [Histórico](../resultados/historico_secoes.json) |
| Seções sem Flávio2026 com até5 votos dele no primeiro turno | **105 de106**, total de **118 votos** | [Histórico](../resultados/historico_secoes.json) |
| Seções com mais de90% dos nominais dos finalistas | Lula **6.802**, Flávio **368** | [Histórico](../resultados/historico_secoes.json) |
| Grupos repetidos de placar nominal / quarteto(L,F,B,N) | **41.133 / 54.304**, estes contendo **117.488 seções** | [Histórico](../resultados/historico_secoes.json) |
| Municípios com comparecimento2026 acima da população do Censo2022 | **120**; Flávio venceu em **45** | [Municípios](../resultados/municipios.json) |
| Comparação histórica de comparecimento acima do Censo2022 | Em2022, **52 municípios**, com5.570 ligações verificadas | [Histórico](../resultados/historico_secoes.json) |
| Soma dos excedentes nesses120 municípios | **33.408** | [Municípios](../resultados/municipios.json) |
| Municípios onde votos de Lula superam a população de referência | **3**, todos no Piauí | [Municípios](../resultados/municipios.json) |
| Estados onde Flávio perdeu votos entre turnos | **AC, AM, AP, MA, RR, TO**; Lula em nenhum | [Municípios](../resultados/municipios.json) |
| Abstenção do Nordeste | **18,39% → 16,49%** | [Municípios](../resultados/municipios.json) |
| Parcela de Lula no ganho líquido dos dois finalistas na Região dos Lagos | **95,1%** | [Municípios](../resultados/municipios.json) |
| Comparação com25 municípios semelhantes do RJ | Cerca de **85%**; diferença do cenário **3.025 votos** | [Municípios](../resultados/municipios.json) |
| Araruama: ganhos nominais dos finalistas | Lula **+5.581**, Flávio **+11**; outros candidatos no1ºturno **5.331** | [Municípios](../resultados/municipios.json) |

H07/2026 já havia conferido:106 seções,14.860 votos para Lula,29 sem
brancos/nulos e15.222 comparecimentos. Agora há comparação histórica e outras
contas primárias. Os três municípios do Piauí são Novo Santo Antônio, Jatobá
do Piauí e Aroeiras do Itaim; os valores individuais estão no JSON.

### Limites que realmente mudam a leitura

**Idades:** as contagens conferem. A diferença148.553 não é uma lista de
falecidos. Censo e cadastro têm cobertura, referência de idade e datas
distintas; inclusive aniversários entre as datas impedem tratar96+ como
coorte exata dos100+ de2026. A edição de comparecimento por idade contém
somente o primeiro turno. O segundo não foi preenchido com zero.

**Municípios:** comparecimento eleitoral e população residente de2022 são
medidas diferentes. A ligação usou UF, nomes normalizados e13 aliases
explícitos, com unicidade do código IBGE verificada. Boa Esperança do Norte
ficou sem população correspondente e foi excluída da comparação, sem receber
zero artificial:5.570 dos5.571 municípios foram ligados.

**Saldo:**95,1% é `ganho de Lula / (ganho de Lula + ganho de Flávio)` nos sete
municípios selecionados pelo autor. Não é95,1% dos votos totais nem observação
do destino individual de votos. O cenário dos3.025 é reproduzível, mas não
identifica votos irregulares.

**Repetições:**54.304 é o número de grupos de quartetos de contagens repetidas,
não54.304 cópias idênticas de todo o arquivo digital do boletim. A simulação
do acaso publicada pelo autor ainda não foi reexecutada aqui. No histórico2018,
o detalhe tem status de instalação/anulação desconhecidos; o resultado com
esses filtros não foi fabricado e permanece `null`. A contagem328 é a do
universo brasileiro com votos nominais positivos, com o limite declarado.

**Categorias e versões:** o ZIP nominal é de03/11 e o detalhe de26/10,
ambos identificados por hash. Em Araruama, o complemento
`comparecimento − válidos` cai1.085, como na referência. Os campos explícitos
de brancos+nulos do detalhe caem1.080; há5 nominais não válidos ou diferença
de edição no primeiro turno. Não escondemos essa diferença nem chamamos
automaticamente todo voto não válido de branco/nulo.

## Contas refeitas nas bases preservadas pelo autor

Esta é outra camada de evidência. Nós escrevemos o cálculo, mas usamos o
Parquet e as respostas oficiais históricas que o autor preservou. Não equivale
a baixar e reconstruir todos os boletins/logs de origem.

| Conta | Recálculo próprio | Alcance |
|---|---|---|
| Corte de encerramento em hora local, com exterior | **52,39%** para Flávio | Repete o universo que reproduz o relatório citado |
| Corte convertido pelo método de abertura, Brasil sem exterior | **50,99%** para Flávio | Corte até17h00min59; não são universos iguais |
| Comparecimento do dia inteiro em seções encerradas a partir de17h16 | **2.537.055** | Não é número de votos lançados depois das17h |
| Eventos de liberação pela digital do mesário | **8.615.564** | Contagem nos campos preservados |
| Liberações sem digital cadastrada, outra categoria | **7.242.863** | Não somar como pessoas fraudulentas |
| Avisos «já votou» | **113.315** | Eventos, não113.315 casos individuais comprovados |
| Versões nacionais capturadas | **346**, nenhuma redução nominal de qualquer finalista | Só a série preservada; não garante intervalos sem captura |

[Resultados completos e hashes](../resultados/capturas.json).
O percentual50,99 também é maior que50; não seria correto dizer que corrigir
o recorte faz desaparecer toda liderança inicial do candidato.

Há uma diferença de versão relevante em H02: o Parquet/`RESUMO.json` soma
**34.393** eventos após17h; o relatório final usa **34.424**, após ajuste de
**31** no oeste do Amazonas. Recalculamos o primeiro total. O ajuste dos31
ainda requer reconstrução dos logs; não o promovemos só por aparecer no texto.
Há2 registros brasileiros sem esses campos de log no Parquet, informados no
resultado, além de29 encerramentos ausentes no conjunto instalado completo.

A soma dos termos do cenário publicado também fecha:
`34.424+148.553+33.408+113.315+49.110+3.025+246+118=382.199`,
ou **8,63%** da margem4.430.191. Isso valida a aritmética da soma; alguns
insumos ainda não foram reexecutados aqui. Categorias podem se sobrepor e os
cenários foram escolhidos: essa soma não é limite universal de toda fraude
possível nem probabilidade de fraude.

## O que muda no roteiro

O [roteiro R5](roteiro-episodio-r5.md) passa a começar pelas contas que
conferem. Preserva a grade24, o lápis curto, as lousas com blocos, o spoiler
sem autor na abertura e o agradecimento a Gabriel no final.
Cada bloco diferencia resultado numérico, origem da reprodução e conclusão.
A [matriz R5](../analise/grade-validacao-r5.json) mantém as24 hipóteses,
sem reaproveitar como atuais os status da apresentação R4.

R3/R4 e seus recibos continuam como histórico. Esta revisão não modifica nem
substitui os vídeos existentes. A análise ainda não foi incorporada ao
atendimento do Pergunte Aí; o [handoff de dados](pergunte-ai-handoff.md)
prepara esse passo com fontes, consultas e limites verificáveis.

## Reprodução e validação

- [Idade](reproduzir-idade.md), [histórico](reproduzir-historico-secoes.md),
  [municípios e capturas](reproduzir-revisao-ampliada.md).
- Python3.12; biblioteca padrão para fontes primárias. Somente o leitor do
  Parquet opcional requer `pyarrow`, usado na versão24.0.0 nesta execução.
- Os43 testes da suíte integrada passaram. [Resumo e hashes da execução](../resultados/revisao_ampliada.json).
  Testes e conferências foram feitos pelos autores dos novos scripts em FAST;
  não representam QA independente nem auditoria completa do sistema eleitoral.
- Brutos, dados de terceiros, mídia e transcrição integral ficaram fora do Git.
