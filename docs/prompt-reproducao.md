# Prompt para reproduzir a análise

Este é o prompt público apresentado no encerramento do vídeo. Estado atual:
a investigação está em andamento; o controle nacional e H07 foram executados.
H01 e H13 permanecem pendentes; consulte `docs/validacao-primeira-rodada.md`.
Reproduzir um estudo não significa aceitar antecipadamente sua conclusão.

Copie o texto abaixo para uma ferramenta de IA que consiga consultar fontes
públicas e executar Python, ou use-o como plano de trabalho manual:

```text
Quero reproduzir de forma independente a análise eleitoral deste projeto:
https://github.com/impactro/alp_analise_eleicoes_2026

Comece lendo README.md, docs/metodo.md, fontes/manifesto.json,
analise/alegacoes.json, docs/estado-inicial.md e
docs/validacao-primeira-rodada.md. Informe o commit consultado.
A referência é o vídeo https://www.youtube.com/watch?v=l5aT6mD0Hpo,
de Gabriel Carvalho, e o projeto original creditado no manifesto.
Considere suas afirmações como alegações a testar.

Use fontes oficiais TSE e IBGE e programas Python inspecionáveis.
Se houver cache ALP autorizado, confira origem, edição, cobertura e hash;
o trabalho também deve poder ser feito sem acesso ao ALP privado.
Não instale dependências nem contorne login, captcha ou restrições de acesso.
Se faltar ferramenta ou evidência, informe exatamente o que ficou pendente.

Primeiro reproduza os totais nacionais com scripts/conferir_totais.py.
Depois reproduza H07 com scripts/conferir_secoes.py e docs/reproduzir-secoes.md.
Examine H01 (horário e fuso) e H13 (cadastro, idade e comparecimento), ainda
pendentes nesta rodada. Documente as demais alegações
separadamente; não transforme análise parcial em auditoria completa.

Para cada alegação, registre: enunciado, timestamp, fonte/URL, data de referência,
geração e SHA-256, universo, cargo/turno, filtros, unidade, denominador,
fórmula, código executado, resultado, diferença para a referência e limitações.
Separe Brasil e exterior, município TSE e código IBGE, voto nominal válido e bruto,
comparecimento e cadastro, horário local e Brasília. Preserve ausências e
unidades não pareadas; não as transforme automaticamente em zero.

Procure reproduzir a mesma edição da fonte. Se só houver edição atualizada,
identifique a diferença e não force concordância. Recalcule controles importantes
por caminho distinto; não trate a repetição do mesmo código como revisão independente.

Não infira óbito ou voto de pessoa falecida pela diferença entre cadastro e Censo.
Não infira transferência individual de voto a partir de saldos municipais.
Não conclua fraude ou integridade eleitoral somente por coincidência estatística.
Não some hipóteses sobrepostas nem confunda cenários com probabilidades.

Entregue uma tabela das 24 afirmações, com uma proposição delimitada por linha:
VERDADEIRO, FALSO ou NÃO É POSSÍVEL VERIFICAR. Acrescente a evidência, o recorte
e, nos itens em aberto, o dado ou teste necessário para verificar.
FALSO exige evidência que contradiga a mesma proposição; falta de arquivo não
é falsidade. NÃO É POSSÍVEL VERIFICAR significa com o material desta rodada,
sem afirmar impossibilidade permanente. Não invente casos falsos para equilibrar
o placar. Quando uma alegação mistura várias contas, separe seus componentes.
H07/2026 reproduzida não confirma comparadores históricos; aritmética H13
correta não valida cadastro, óbitos ou comparecimento. Preserve também o estado
técnico: reproduzido, divergente, parcialmente testável ou pendente.
Use analise/grade-validacao-r4.json como mapa de apresentação, não como prova.
Construa gráficos com unidades,
fontes e escalas legíveis. Registre correções e lacunas, sem preencher dados inventados.

Publique somente código próprio, método, fontes, hashes e pequenos resultados
agregados revisados. Dados brutos, bancos, mídias, transcrição integral,
credenciais e conversas ficam fora do Git. Não execute código de terceiros
nem publique ou atualize serviços sem autorização específica.
```

Para buscar igualdade numérica, fixe também o commit usado no episódio e os
hashes de entrada. O mesmo prompt aplicado a uma edição diferente pode gerar
um resultado diferente. A IA ajuda a trabalhar; a evidência continua sendo a
fonte, o programa e a execução conferível.
