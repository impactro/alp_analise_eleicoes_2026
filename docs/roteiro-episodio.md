# Eleitores mortos? Abrimos os dados e refizemos as contas

Roteiro próprio da CrânIA, episódio extra 2026-11-04-B, revisão 2.
Texto aprovado para narração; produção audiovisual em andamento.
A análise usada é o commit `5015bae190b14cececc9ef9445f7aeea9e7a895e`.
Controle nacional e H07 reproduzidos; H01/H13 permanecem pendentes.

## A pergunta que virou projeto

Eleitores mortos votaram no segundo turno? Essa pergunta apareceu no vídeo de Gabriel Carvalho e abriu uma investigação com vinte e quatro hipóteses. Em vez de responder pela torcida, nós abrimos os arquivos e refizemos parte das contas. Já temos um resultado concreto: as cento e seis seções sem voto para Flávio aparecem no nosso programa também. Mas o que esse número conta? E o que ele ainda deixa sem resposta? Eu sou a Crânia. Este é um episódio extra para começar uma série em que você pode acompanhar a fonte, executar o programa e discutir o resultado. A conta vai ficar aberta.

## O controle nacional

A primeira conta foi o controle nacional. No arquivo oficial de votação por município e zona, somamos separadamente Brasil e exterior. No segundo turno, Lula teve sessenta e quatro milhões, duzentos e cinquenta e seis mil, duzentos e trinta e dois votos. Flávio teve cinquenta e nove milhões, oitocentos e vinte e seis mil e quarenta e um. A diferença é de quatro milhões, quatrocentos e trinta mil, cento e noventa e um votos. Essa edição da base foi gerada em três de novembro. Nosso programa lê um único arquivo nacional e evita somar novamente as cópias por estado. Assim, o mesmo voto não entra duas vezes no controle.

## Antes da interpretação, a unidade

Agora separe quatro coisas: cadastro, comparecimento, voto e população. Cadastro é a lista de pessoas aptas. Comparecimento é a presença registrada na eleição. Voto é a escolha contabilizada, que também pode ser branco ou nulo. População residente é outra medida, coletada com outra finalidade e outra data. Uma pessoa cadastrada pode faltar. Uma pessoa que comparece pode votar em branco. E a diferença entre duas populações agregadas não revela a identidade de ninguém. Essas distinções parecem pequenas até alguém trocar uma pela outra e transformar uma pergunta em certeza. Para investigar, o primeiro passo é escrever o que cada coluna realmente mede.

## Como refizemos a conta das seções

Para conferir as seções com votação zero, usamos dois arquivos oficiais: votação por seção e detalhe da votação. O programa identifica cada seção pela unidade da federação, município, zona e número da seção. Depois seleciona presidente, segundo turno e Brasil, sem exterior. Entram seções instaladas, não anuladas e com votação nominal positiva. Uma linha ausente no arquivo de um candidato não vira zero automaticamente: primeiro reconstruímos os totais e conferimos se o conjunto fecha com o detalhe. Nesse recorte, foram quase quatrocentas e noventa e oito mil seções e mais de cento e vinte e três milhões de votos nominais reconciliados. Os dois arquivos usados foram gerados em vinte e seis de outubro.

## Os três números que conferem

O resultado foi de cento e seis seções sem voto para Flávio. Nessas seções, Lula recebeu quase quinze mil votos, exatamente como na contagem de Gabriel. Em vinte e nove delas, também não houve voto branco ou nulo. O comparecimento total passou de quinze mil pessoas. Os valores exatos estão no resultado aberto e no material do episódio. Aqui a conferência saiu do discurso: há um programa próprio, arquivos identificados e um resultado que pode ser repetido. Estamos falando de seções, não de municípios. E vinte e nove é parte da contagem inicial, não uma quantidade que se soma a ela.

## Quando o número vira hipótese

Encontrar uma seção com zero voto para um candidato é uma observação. Decidir se isso é inesperado exige uma comparação. Quantos eleitores havia ali? Qual era o apoio ao candidato naquela região? O padrão se repete em outras eleições? Uma conta que trata todas as seções como sorteios idênticos ignora que os eleitores vivem em lugares diferentes e têm preferências diferentes. Nosso programa desta rodada ainda não fez a comparação histórica. Portanto, o resultado publicado é a reprodução da contagem. Para testar uma explicação, o próximo passo é definir a comparação antes de olhar a resposta e registrar também os casos que não combinam com a hipótese.

## Cadastro não é certidão de óbito

No bloco sobre idade, o vídeo compara duzentos e noventa e sete mil, novecentos e setenta e sete eleitores com cem anos ou mais, com cento e quarenta e nove mil, quatrocentos e vinte e quatro residentes de noventa e seis anos ou mais no Censo de dois mil e vinte e dois. A subtração dá cento e quarenta e oito mil, quinhentos e cinquenta e três. A aritmética está certa. Os dois totais de origem ainda não foram reproduzidos por nós. Mesmo com os totais confirmados, essa diferença não identificaria pessoas falecidas. São agregados com datas e conceitos diferentes. Para afirmar que uma pessoa morta votou, seria preciso estabelecer a identidade, o óbito anterior à votação e o registro de comparecimento correspondente. A diferença entre totais não fornece essa ligação. É justamente essa passagem, do agregado para uma pessoa concreta, que o título coloca em discussão.

## Os relógios também precisam de contexto

Há outra pergunta no vídeo: o recorte de horários que produz cinquenta e dois vírgula trinta e nove por cento para Flávio. Para refazer essa conta, precisamos do horário de abertura e de encerramento de cada seção e da regra de fuso aplicada a cada lugar. Horário de recebimento de um boletim não é horário de encerramento da votação. E o encerramento de uma seção não informa a hora em que cada eleitor votou. Essa reprodução continua pendente no nosso projeto. Você verá essa marcação no repositório. A pergunta fica aberta com a indicação do dado que falta, em vez de receber um resultado calculado com o relógio errado.

## O que a inteligência artificial faz aqui

Esse trabalho também mostra como Fábio Souza aplica inteligência artificial: organiza contexto, conecta ferramentas e transforma uma pergunta em uma investigação que outra pessoa pode conferir. O Pergunte Aí é um ambiente para estudar e explorar dados em linguagem comum. A pergunta ajuda a encontrar um caminho; o programa registra como a conta foi feita. No projeto aberto, você encontra o método, os filtros e os resultados pequenos que cabem em uma revisão. Esse é o convite para conhecer os trabalhos do Fábio: inteligência artificial aplicada com contexto, execução e supervisão humana. O estudo continua quando alguém encontra uma pergunta melhor.

## O que esta rodada entrega

Nesta primeira rodada, conferimos o controle nacional e reproduzimos a contagem das seções sem voto para Flávio. A comparação de idade e o recorte de horários continuam com os insumos e os testes pendentes identificados. As vinte e quatro hipóteses do vídeo original não estão todas validadas. Cada uma terá seu próprio resultado. O repositório guarda o código, a origem dos arquivos, suas versões e pequenas evidências agregadas. Os arquivos brutos ficam fora do Git. Você baixa a fonte e executa a mesma conta. Se a fonte mudar, o programa identifica que os bytes são outros e a nova execução precisa registrar essa diferença.

## O prompt e o GitHub

Quer fazer a mesma análise? Peça à sua inteligência artificial: reproduza esta análise eleitoral com fontes oficiais, Python e cálculos independentes. Confira versões, filtros, unidades e denominadores. Separe cálculo, hipótese e conclusão. Mostre o que confere, o que diverge e o que os dados não permitem concluir. Publique método e código e mantenha os arquivos brutos fora do Git. O prompt completo e os programas estão no GitHub, no projeto alp análise eleições dois mil e vinte e seis. O endereço está na descrição e no material do episódio. Você também pode levar as perguntas para estudar no Pergunte Aí.

## Agradecimento e convite

Gabriel Carvalho, obrigado pela ideia, pelo estudo e pela narrativa que inspiraram esta investigação. Seu vídeo e seu projeto original estão na descrição. Juntos, com inteligência natural, podemos vencer a burrice artificial implantada na humanidade. Porque só o conhecimento liberta. Compartilhe e siga para muito mais!

## Fontes e reprodução

- [Controle nacional](../resultados/controle_nacional.json) — edição 03/11/2026.
- [H07 por seção](../resultados/secoes_zero_voto.json) — edição 26/10/2026.
- [Relatório desta rodada](validacao-primeira-rodada.md).
- [Prompt integral](prompt-reproducao.md).
- [Vídeo de Gabriel Carvalho](https://www.youtube.com/watch?v=l5aT6mD0Hpo) e [projeto original](https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026).

Os valores de 14.860 votos e 15.222 comparecimentos são exatos nas evidências; na fala do bloco correspondente, usamos quase 15 mil e mais 15 mil, respectivamente. O arredondamento verbal não altera os resultados publicados.

Crédito musical previsto: Long Note Three, Kevin MacLeod, CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
