# H07: seções sem voto e comparação histórica

O [resultado agregado](../resultados/historico_secoes.json) foi calculado por
[código próprio](../scripts/conferir_historico_secoes.py), em Python 3.12 e
biblioteca padrão, diretamente de seis ZIPs oficiais do TSE. Não executa os
programas do autor nem lê seus Parquets. A referência é a função de H07 em
[`ferramentas/analise.py`, revisão 4a12ed0](https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026/blob/4a12ed014cf7927df24226f900450db7fe5b1a22/ferramentas/analise.py).

## Resultado

| Eleição, segundo turno | Brasil sem exterior: seções sem voto para o candidato | Incluindo exterior | Votos do adversário nessas seções, Brasil |
| --- | ---: | ---: | ---: |
| 2018, Bolsonaro | 328 | 328 | 36.608, Haddad |
| 2022, Bolsonaro | 141 | 143 | 16.418, Lula |
| 2026, Flávio | 106 | 106 | 14.860, Lula |

As três contagens brasileiras coincidem com o resultado do estudo original.
Em 2022, acrescentar o exterior muda 141 para 143: é necessário declarar o
recorte. Nas 106 seções de 2026, também se reproduziram 15.222 comparecimentos
e 29 seções sem votos brancos e nulos.

No primeiro turno de 2026, as 106 chaves de seção foram encontradas com votação
positiva. Flávio teve 118 votos no conjunto: 50 seções com zero, 55 com um a cinco
e uma com 16. Portanto, **105 de 106 tiveram até cinco votos para ele**.
Isso descreve agregados nas mesmas chaves; não permite acompanhar pessoas ou
inferir para quem cada eleitor votou entre os turnos.

Nas mesmas chaves de 2026, foram encontradas 61 seções com votação nominal
positiva em 2022, somando 103 votos para Bolsonaro; 23 delas tiveram zero.
Em 2018, foram encontradas 47, somando 55 votos para ele; 21 tiveram zero.
Chaves não encontradas não viram votos zero. Uma chave coincidente não garante
o mesmo eleitorado nem a mesma composição de seção.

A expressão de busca usada pelo autor, aplicada ao nome do local do detalhe
oficial, encontrou **46 das 106 seções (43,4%)**, também coincidindo com o
resultado publicado por ele. A expressão inclui `INDIGENA`, `ALDEIA`, `INDIG`,
`TERRA INDIGENA`, `QUILOMB`, `KM `, `MALOCA`, `COMUNIDADE`, `POLO BASE`,
`POSTO DE SAUDE` e `SESAI`, após retirar acentos e converter para maiúsculas.
Isso reproduz uma busca textual ampla; `KM` ou `POSTO DE SAUDE`, por exemplo,
não comprovam a existência de uma comunidade indígena. Não se classificou a
identidade étnica de eleitores.

## Recorte, integridade e status

O programa lê apenas `*_BR.csv` em cada arquivo, nunca soma `BRASIL.csv` nem os
membros por UF. Filtra eleição ordinária, presidente, segundo turno e as 27 UFs,
exibindo também uma variante com `ZZ` (exterior). A chave é
UF/código de município/zona/seção, sem cruzar zonas de municípios diferentes.
Número 17 identifica Bolsonaro em 2018; 22 identifica Bolsonaro em 2022 e
Flávio em 2026; 13 identifica Haddad ou Lula conforme o ano.

Uma opção ausente só é tratada como zero dentro de uma seção que tem votos
nominais positivos para o adversário. Seção ausente inteira, somente com
brancos/nulos ou sem votação nominal não é incluída como seção unânime.
Duplicatas de seção/opção são rejeitadas, assim como valores negativos,
opções inesperadas e múltiplas edições dentro do membro nacional.

Os detalhes de 2022 e 2026 permitem filtrar instalação e anulação e reconciliar
votos nominais, brancos, nulos, comparecimento e aptos por seção. As contagens
141 e 106 permanecem iguais depois desse filtro. Não há seção com voto nominal
positivo sem detalhe correspondente.

Em 2018, os campos de status da edição de detalhe são `#NULO#`: o programa
registra status desconhecido e devolve `null` para a variante com status
confirmado. Isso não significa seção não instalada nem contagem zero.
O número 328 é a contagem com votação nominal positiva no arquivo de votação;
a documentação não o apresenta como confirmação de instalação/anulação.

## Conferência municipal adicional de 2022

Com a opção `--population-json`, o programa soma comparecimento por município
nas seções instaladas e não anuladas do segundo turno de 2022. Compara com a
população residente total municipal do Censo 2022, variável 93, tabela 9514 do
IBGE. A resposta primária e seu SHA-256 ficam identificados no JSON.

A junção usa UF e nome sem acentos, pontuação ou espaços, preservando os
aliases explícitos de `scripts/conferir_municipios.py`. Foram acrescentadas
duas correspondências históricas locais: Camacã (BA, código TSE 34118) para
Camacan; Santa Isabel do Pará (PA, código TSE 5290) para Santa Izabel do Pará.
O código TSE é verificado antes de aplicar esses dois aliases. As grafias
atuais e os códigos IBGE 2905602 e 1506500 também foram conferidos no cadastro
público de municípios do TSE, em leitura. O resultado registra aliases e
qualquer ausência; população ausente nunca vira zero.

As 5.570 localidades de 2022 tiveram correspondência, sem ausência. Foram
reproduzidos os **52 municípios** com comparecimento superior à população
residente total do Censo 2022, como na referência.

Esses conceitos precisam ser lidos com cuidado: domicílio eleitoral e
residência censitária são diferentes. Comparecimento superior à população
residente, isoladamente, não demonstra voto irregular.

## Saturação e placares repetidos em 2026

O mesmo conjunto elegível de seções de 2026 também alimenta H04 e a parcela
descritiva de H08, no campo `sectionDistribution` do JSON. H04 conta participação
**estritamente maior que 90% dos votos nominais**, usando comparação inteira
para preservar a fronteira de exatamente 90%.

Reproduziram-se **6.802 seções para Lula e 368 para Flávio** acima desse limite.

Para H08, o programa conta grupos observados com pelo menos duas seções, tanto
do par `(Lula, Flávio)` quanto do quarteto `(Lula, Flávio, brancos, nulos)`.
Registra separadamente o número de grupos e o número de seções participantes,
além de grupos dentro de um mesmo município ou zona. O quarteto reproduz a
definição de `identicas()` em
[`rodada_3.py`, revisão fixada](https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026/blob/4a12ed014cf7927df24226f900450db7fe5b1a22/ferramentas/rodada_3.py).
Embora o original o chame de boletim inteiro repetido, são quatro contagens,
não todos os campos do arquivo de um boletim de urna. Esta reprodução não
executa simulação de acaso nem teste de significância; frequência observada
não demonstra que a repetição seja anormal.

Foram reproduzidos **41.133 grupos de placares nominais repetidos** e
**54.304 grupos de quartetos repetidos**, estes envolvendo 117.488 seções.
Dentro do mesmo município foram 949 grupos de quartetos; dentro da mesma
zona, 212. Grupos e seções são unidades de contagem diferentes.

## Reproduzir

Baixe para uma pasta local fora do Git os arquivos das seis URLs em `sources`
no JSON: `votacao_secao_{ano}_BR.zip` e
`detalhe_votacao_secao_{ano}.zip`, para 2018, 2022 e 2026. Preserve os nomes.
Hashes, tamanhos e datas de geração constam no resultado. O programa compara
os seis SHA-256 com as edições fixadas e falha se a fonte mudar. O fuso das datas
de geração não foi informado pela fonte e permanece `null`.

Na raiz deste repositório:

```text
python -s -m scripts.conferir_historico_secoes --data-dir local/brutos/historico --output local/historico_secoes.json
python -s -m unittest tests.test_historico_secoes tests.test_secoes -v
```

Para incluir a comparação municipal de 2022, baixe a resposta da URL
`sources.ibgeCensus2022.url` e execute:

```text
python -s -m scripts.conferir_historico_secoes --data-dir local/brutos/historico --population-json local/brutos/populacao-municipal-total-2022.json --output local/historico_secoes.json
```

Os ZIPs de detalhe são opcionais para as contagens históricas de votação, mas
o detalhe de 2026 é necessário para o conjunto elegível que fundamenta o
cruzamento do primeiro turno e a busca nos nomes. Sem um detalhe, o programa
registra a indisponibilidade de status. O resultado publicado usou os seis.

O comando não baixa arquivos, extrai ZIPs, chama modelos, instala dependências
nem modifica a fonte. Usa CPU para CSV/ZIP, sem operação que se beneficie de
CUDA. Os testes são conferência do próprio desenvolvedor, incluindo filtros,
duplicação, reconciliação, ausência de seção e status desconhecido. Não são
validação independente.

Resultados eleitorais agregados não identificam eleitores, mortes ou
transferências individuais de voto e não demonstram fraude nem certificam a
integridade de uma eleição.
