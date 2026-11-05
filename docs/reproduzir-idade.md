# Conferir idade e comparecimento (H13)

Programa próprio, em Python 3.12 com biblioteca padrão. Não executa código do
autor, não consulta bancos privados e não identifica eleitores. Lê ZIPs sem
extraí-los e emite JSON para stdout. As fontes brutas ficam fora do Git.

A referência é o [estudo de Gabriel Carvalho, revisão fixada](https://github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026/tree/4a12ed014cf7927df24226f900450db7fe5b1a22),
em especial `ferramentas/analise.py`, função `h13_h14`, e
`ferramentas/ibge.py`. O código foi lido para definir o teste; a implementação
desta conferência foi escrita separadamente.

## Fontes e execução

Baixe as três fontes para uma pasta local ignorada pelo Git, por exemplo
`local/idade/`. Os comandos abaixo usam `curl` e nomes relativos à raiz do
projeto. No Windows PowerShell, use `curl.exe` se `curl` for um alias.

```text
curl --fail --location "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitorado/perfil_eleitorado_2026.zip" --output local/idade/perfil_eleitorado_2026.zip
curl --fail --location "https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_2026.zip" --output local/idade/perfil_comparecimento_abstencao_2026.zip
curl --fail --location "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93?localidades=N1%5B1%5D&classificacao=2%5B6794%5D%7C286%5B113635%5D%7C287%5B6649%2C6650%2C6651%2C6652%2C6653%5D" --output local/idade/ibge_n1.json
python -s scripts/conferir_idade.py --electorate-zip local/idade/perfil_eleitorado_2026.zip --electorate-sha256 0952e9d9577be19380b444bfcc6a9a99397005e8dc839de9d5ec49914d75648b --attendance-zip local/idade/perfil_comparecimento_abstencao_2026.zip --attendance-sha256 abd1af8ff28a80b4e861edafd9f544a8f3f667e1c2e146911d083bf7cc34f023 --census-json local/idade/ibge_n1.json --census-sha256 e8a4d2de5dccc9accfe3ae8e7d06b66f16a33ecd67273ecae16d5e5746844bd3
python -s -m unittest tests.test_idade -v
```

O leitor precisa criar a pasta de destino antes do download. O resultado
publicado está em [idade.json](../resultados/idade.json). O programa sempre
confere o SHA-256 antes de calcular. Uma alteração nas fontes exige registrar
e revisar uma nova edição, sem trocar o hash apenas para fazer a execução passar.
Resposta JSON equivalente, mas com outra serialização, também terá outro hash.

## Recorte e contas

Para cada ZIP, a leitura usa somente o membro `BRASIL.csv`; os arquivos por UF
que repetem seu conteúdo não entram na soma. Na ausência do membro nacional,
exige o conjunto completo das 27 UFs e do exterior. Os resultados eleitorais
principais excluem `ZZ`, e o resultado informa separadamente o cadastro de
centenários no exterior. O programa valida ano, UF, código e descrição da faixa
etária, quantidades não negativas e, nas faixas estudadas, a igualdade
`aptos = comparecimento + abstenção`. Lê a lista efetiva de turnos do arquivo.

A tabela IBGE 9514 usa a variável 93 (população residente), sexo total
`2[6794]`, forma de declaração da idade total `286[113635]` e as categorias
`287[6649,6650,6651,6652,6653]`: 96, 97, 98, 99 e 100 anos ou mais.
A consulta nacional `N1[1]` respondeu nesta rodada; não foi necessário usar as
capturas municipais do autor como substituto. Exigem-se as cinco idades,
uma série nacional por idade e o período 2022, sem valores ausentes/suprimidos.

As duas comparações têm sentidos diferentes:

- Cadastro de 100 anos ou mais em 2026 menos residentes de 96 anos ou mais
  em 2022: aproximação agregada de coorte, quatro anos antes.
- Cadastro de 100 anos ou mais em 2026 menos residentes de 100 anos ou mais
  em 2022: mesma faixa de idade nominal, em datas diferentes. Não acompanha
  a mesma coorte.

A taxa de comparecimento usa o total de aptos da própria tabela de
comparecimento para a faixa e o turno. O JSON também registra a razão com o
cadastro biométrico, que é apenas outra divisão agregada: não demonstra que
aqueles votantes tenham usado biometria no dia.

## Resultado desta edição

As fontes primárias reproduziram as quatro parcelas nacionais solicitadas da
referência: **297.977** registros de 100 anos ou mais em 2026, **149.424**
residentes de 96 anos ou mais no Censo 2022, diferença de **148.553** e
**2.141** comparecimentos de centenários no primeiro turno, ou **0,72%** dos
297.977 aptos dessa faixa. O Censo 2022 contou **37.814** pessoas de 100 anos
ou mais; a diferença com o cadastro de 2026 na mesma faixa nominal é 260.163,
uma comparação entre datas distintas, sem acompanhamento individual.

| Faixa etária em 2026 | Aptos | Comparecimento no 1º turno | Taxa |
| --- | ---: | ---: | ---: |
| 85 a 89 anos | 1.464.715 | 356.147 | 24,32% |
| 90 a 94 anos | 664.482 | 89.530 | 13,47% |
| 95 a 99 anos | 337.136 | 14.661 | 4,35% |
| 100 anos ou mais | 297.977 | 2.141 | 0,72% |

A tabela de comparecimento tem geração interna em **13/10/2026 às 16:46:32**;
a de eleitorado, em **14/07/2026 às 18:03:33**. Foram lidas 11.060.908 e
11.046.845 linhas nacionais, respectivamente, incluindo o exterior antes do
recorte. O primeiro arquivo contém somente o **turno 1**. A consulta foi feita
em 05/11/2026; a data de download não torna a edição mais recente. A conclusão
de ausência do turno 2 se limita ao arquivo identificado pelo hash.

## Limites de interpretação

As contagens não identificam mortos. Cadastro eleitoral e população residente
têm datas, critérios e cobertura diferentes. Envelhecimento exato entre as
datas, óbitos, migração, cobertura censitária e erro de declaração de idade
não são resolvidos pela subtração. Portanto, a diferença numérica não deve ser
chamada de quantidade comprovada de eleitores falecidos ou registros
individualmente impossíveis.

Há também um detalhe de calendário: a [referência do Censo](https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html?edicao=38166&t=resultados)
é a noite de 31/07 para 01/08/2022, enquanto o [primeiro turno de 2026](https://www.tse.jus.br/eleicoes/cde-2026)
ocorreu em 04/10. Inferência: se a idade eleitoral estiver referida ao dia do
pleito, parte de quem tinha 95 anos no Censo já poderia ter completado 100.
Não foi verificada nesta fatia a data de referência exata da idade cadastral;
isso reforça o caráter aproximado da comparação 96+ versus 100+.

Ausência de segundo turno nessa edição é ausência de dado. A comparação do
primeiro turno não responde quem compareceu no segundo turno, nem em quem
essas pessoas votaram. Esta fatia não reproduz os cruzamentos municipais nem
os arquivos eleitorais de 2022 usados pelo autor.

Os testes verificam recortes, prevenção de dupla contagem, categorias censitárias,
reconciliação, denominador e tratamento de turno ausente. São testes do próprio
desenvolvedor; não constituem QA independente.
