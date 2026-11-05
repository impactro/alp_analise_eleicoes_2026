# Reproduzir municípios e capturas

Os scripts são nossos; não importam código do autor nem dependem do Pergunte Aí.
Crie `local/municipios/` e baixe os três endereços de
[`municipios.json`](../resultados/municipios.json), preservando seus bytes.
Os ZIPs podem mudar no servidor; uma nova edição deve receber manifesto e
comparação próprios. JSON semanticamente igual com outra serialização também
muda de hash. Não troque o hash apenas para silenciar a checagem.

```text
python -s scripts/conferir_municipios.py --votes local/municipios/votacao_candidato_munzona_2026.zip --votes-sha256 6d60a212fc46541fbf605da38ad1fcdd83deda030b802e70405ba6b9a01289c1 --detail local/municipios/detalhe_votacao_secao_2026.zip --detail-sha256 8ef9ce3a85cde260471faf7a83a9b4f5ccf3993fdda942aacaa658574344789c --population local/municipios/ibge-pop-total-2022.json --population-sha256 8afacb4f4dd0fa0779431f3ba52c73f580e3b2219ee0a9829c045cdcf3f9b5da
```

O script usa só os membros `_BR.csv`: não soma os arquivos por UF ou
`BRASIL.csv` que repetem linhas. Separa o exterior e guarda a geração interna
de cada entrada. Agrega os votos nominais válidos por município/zona/destinação,
os detalhes por seção, e valida `aptos=comparecimento+abstenções`. Há13 aliases
de grafia declarados em `NAME_ALIASES`; os códigos IBGE ligados e o município
sem ligação aparecem no resultado. Não há correspondência aproximada ou valor
populacional imputado. Os cálculos de regiões usam soma de numeradores e
denominadores, não média simples de percentuais municipais.

O cruzamento combina nominais de03/11 com detalhe de26/10, edições fixadas.
Os resultados devem ser lidos nesse contexto. A diferença de5 nominais não
válidos/edição em Araruama fica visível, sem forçar a reconciliação entre
categorias distintas. Os arquivos primários não estão neste repositório.

## Tabelas e versões preservadas pelo autor

Baixe a revisão fixa do projeto original em
`https://codeload.github.com/Gabriel-Alexandre/investigacao-hipoteses-segundo-turno-2026/zip/4a12ed014cf7927df24226f900450db7fe5b1a22`.
O ZIP usado teve134.197.573 bytes e SHA256
`f3a1378864bcc7085f24943c099afe649d7de7e8d304ffe809833936fac0a9b1`.
Extraia em `local/autor/`, ajustando a pasta superior do ZIP. Não execute
scripts do arquivo. Precisamos somente do Parquet e dos346 JSONs nacionais.
O restante serve para inspecionar as fontes e o método.

O leitor de Parquet opcional usa `pyarrow` (24.0.0 na execução publicada).
Os outros programas e os testes não precisam dele.

```text
python -s scripts/conferir_capturas.py --parquet local/autor/dados/copias/t2_secoes.parquet --parquet-sha256 6da34ba9791e1f06ab12fa5e4b7f62ea882178e2e1600e99a8e7ab3ec2fd80e4 --national-captures local/autor/dados/copias/noite/versoes-tse/br
python -s -m unittest discover -s tests -v
```

O cálculo usa o campo de encerramento, não o recebimento do BU. A conversão
reproduz o método documentado de inferir a diferença de fuso pela abertura;
não é uma auditoria independente dos fusos. O resultado informa campos
ausentes e offsets de fallback. O corte é estritamente antes de17h01.
A série é ordenada por data/hora de geração e ID da versão, sem preencher
versões ausentes; redução de percentual não vira redução de voto nominal.
O selo do conjunto é SHA256 do JSON compacto de uma lista ordenada por nome,
cada elemento com `name` e `sha256`, chaves ordenadas, conforme o script.

Recálculo da tabela preservada, confirmação em fonte primária e conferência
aritmética são camadas diferentes. Consulte
[a revisão e suas divergências](revisao-ampliada.md).
