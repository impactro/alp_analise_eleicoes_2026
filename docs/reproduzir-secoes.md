# Reproduzir a contagem de seções sem voto para Flávio

Implementação original, Python 3.12, somente biblioteca padrão. Não utiliza
código do projeto de referência, banco ALP, login nem dependência de terceiros.

Baixe os dois ZIPs nos links de `sources` de
`resultados/secoes_zero_voto.json`. Guarde os brutos fora do Git. A execução
de referência usou arquivos locais já existentes, sem novo download:

```powershell
python -s scripts/conferir_secoes.py --detail-zip <detalhe.zip> --votes-zip <votacao.zip> --detail-sha256 8ef9ce3a85cde260471faf7a83a9b4f5ccf3993fdda942aacaa658574344789c --votes-sha256 c928321f63f2d095706fca73d4607c048d2ada23bda6876455d6911aaf1bc9c1 --output resultados/secoes_zero_voto.json
python -s -m unittest discover -s tests -v
```

Substitua os argumentos entre `< >` pelos arquivos baixados. Se a fonte
tiver sido atualizada e o hash mudar, preserve a edição anterior para
comparação ou produza um resultado de edição nova sem o hash esperado.
Não sobrescreva silenciosamente a evidência que fundamentou o episódio.

O programa lê somente o membro nacional `_BR.csv` de cada ZIP, sem extrair
os arquivos. Não soma `_BR` com os membros estaduais. Filtra eleição ordinária
de 2026, presidente, segundo turno e 27 UFs; o exterior fica fora desta conta.
O universo inclui seções instaladas, não anuladas e com nominal positivo.
A chave é UF, código municipal TSE, zona e seção.

Para cada seção, a soma de Lula e Flávio precisa igualar os votos nominais
do detalhe. Brancos, nulos, comparecimento e aptos também são conferidos.
Uma linha ausente para Flávio só vira zero depois dessa reconciliação.
Detalhe ou voto duplicado, opção inesperada e contagem incompatível causam
erro. Resultado vazio não vira uma conclusão estatística.

Nesta edição, 497.897 seções e 123.710.622 votos nominais reconciliaram.
Foram contadas 106 seções sem voto para Flávio, com 14.860 votos para Lula,
15.222 comparecimentos e 29 seções sem brancos ou nulos.
Os 362 comparecimentos restantes correspondem a brancos/nulos nesse conjunto.
O total de votos das seções não deve ser confundido com a quantidade de seções.

O teste usa dados sintéticos pequenos e cobre ausência indevida de votação,
duplicidade, reconciliação e exclusão do exterior. Não há bruto nem identificação
de eleitor no repositório. Comparadores de 2018/2022 e comportamento individual
não foram testados nesta rodada. Esta contagem sozinha não demonstra fraude
nem certifica integridade eleitoral.
