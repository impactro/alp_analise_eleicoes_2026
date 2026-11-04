# Método de validação

## Pergunta antes da conclusão

Comparar o enunciado do vídeo, sua fonte e o cálculo independente. Não montar
duas IAs para votar qual narrativa parece melhor. Modelos podem ajudar a
formular hipóteses e revisar código; o resultado vem de dados e operações
verificáveis. Divergência pode ser revisão da fonte, cobertura ou erro: investigar.

## Estados por alegação

- `pending`: extraída, mas ainda sem cálculo independente.
- `reproduced`: valor reproduzido na mesma população e versão.
- `divergent`: diferença material após conciliar definição e versão.
- `partially_testable`: apenas parte do enunciado é observável nos dados acessíveis.
- `not_testable_with_available_data`: a evidência necessária não está disponível.

Esses são estados de trabalho da análise. Não são vereditos sobre uma eleição.
Uma conclusão interpretativa deve ter campo próprio e explicar o alcance.

## Fontes, versões e granularidade

1. Usar o vídeo e o repositório do autor para identificar a alegação, não como
   autoridade primária sobre o resultado eleitoral.
2. Usar TSE e IBGE com período, data de geração, URL e hash. Cache do ALP é
   reutilizável quando a proveniência e a edição forem compatíveis.
3. Primeiro refazer o snapshot da referência; comparar separadamente com fonte
   mais recente. Versões ao vivo precisam de registro contemporâneo: arquivo
   final não reconstrói sozinho a sequência histórica de divulgação.
4. Separar Brasil e exterior, eleição ordinária e suplementar, cargo e turno.
   Município TSE não é código IBGE. Pareamento usa chave/versão territorial,
   nunca apenas nome. Conservar os não pareados.
5. Totais por candidatura não medem comparecimento. Contagem de avisos de log
   não mede pessoas distintas nem votos fraudulentos.
6. Zeros esparsos só são preenchidos depois de provar a seção e seu universo
   completo. Arquivo, seção ou candidato ausente não vira zero automaticamente.
7. Documentar duplicatas legítimas, eleitores em trânsito, mudança de seções,
   anulados, contingência e boletins do sistema de apuração conforme o campo.

## Testes prioritários

**Fuso:** horas locais, horário de Brasília, abertura, encerramento e recepção
são eventos distintos. Usar timezone/correspondência municipal na data do evento;
o oeste do Amazonas não segue a mesma hora de toda a UF. Mostrar sensibilidade
ao corte exato (17:00:00, 17:00:59 etc.) e ao exterior.

**Zero voto:** validar a cobertura completa por seção, contar exclusões,
comparar as mesmas unidades e divulgar o número de pares válidos em cada ano.
Não concluir identidade social do local só por seu nome.

**Idade:** comparar a data de referência e definição de idade em cada base;
população residente não equivale a eleitorado domiciliado. Migração, cobertura,
erros de cadastro/idade e defasagem são hipóteses a examinar. A subtração
297.977 − 149.424 = 148.553 é aritmética reproduzível; ela não identifica
148.553 óbitos. Votar exige evidência de comparecimento na edição/turno correto.

**Transferência:** saldo municipal não identifica trajetória individual do voto.
Uma razão baseada em variações líquidas deve receber esse nome e mostrar
denominador, brancos/nulos, comparecimento e limites da inferência ecológica.

**Impacto:** separar adição, retirada e troca de voto entre candidatos. Uma
troca altera a margem em duas unidades; adição em um lado altera em uma.
Não somar hipóteses sobrepostas como casos distintos. Soma de cenários não é
probabilidade e um cenário escolhido não é limite universal de fraude.

**Amostras:** fixar semente e universo antes de olhar o resultado; publicar
probabilidade de seleção/cobertura, perdas e incerteza apropriada. Não extrapolar
logs selecionados como se cobrissem todas as urnas.

## Aceite e publicação

Cada número exibido deve apontar para fonte, programa, parâmetros, versão e
resultado. Recomputar contas importantes por outra implementação ou identidade
contábil independente, não pela mesma função renomeada. O primeiro controle
usa CSV oficial diretamente e é comparado ao índice ALP, em caminhos distintos;
ambos derivam da mesma origem, portanto isso não é confirmação por outra fonte.

Publicar apenas originais próprios e pequenos resultados agregados revisados.
Repositório acessível não concede licença para copiar código, texto ou mídia
de terceiros. Fontes primárias continuam com suas licenças e atribuições.
