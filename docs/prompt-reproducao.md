# Prompt para reproduzir a análise

Prompt atualizado após a revisão ampliada e a reconstrução temporal de 05/11/2026. Há 8 blocos numéricos
reproduzidos em fontes primárias,5 recalculados nas bases preservadas pelo autor
e outras parcelas pendentes. Consulte `docs/revisao-ampliada.md` e a matriz R5.
O vídeo R4 e sua descrição preservam a versão anterior deste prompt no commit
`ddc63e5`; este arquivo passa a orientar a nova reprodução.
Reproduzir um estudo não significa aceitar antecipadamente sua conclusão.

Copie o texto abaixo para uma ferramenta de IA que consiga consultar fontes
públicas e executar Python, ou use-o como plano de trabalho manual:

```text
Quero reproduzir de forma independente a análise eleitoral deste projeto:
https://github.com/impactro/alp_analise_eleicoes_2026

Comece lendo README.md, docs/metodo.md, fontes/manifesto.json,
docs/revisao-ampliada.md, analise/grade-validacao-r5.json e
docs/linha-do-tempo-divulgacao.md. Use estado-inicial e primeira-rodada como
histórico, não como situação atual. Informe o commit consultado.
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
Confira as parcelas de H01 (horário e fuso) e H13 (cadastro, idade e
comparecimento) já recalculadas e explicite as parcelas causais pendentes.
Documente as demais hipóteses
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
Leia antes a descrição do vídeo, o relatório, os manifestos, os scripts e as
revisões do projeto do autor. Identifique quem propôs cada hipótese e qual
foi a conclusão original. São24 hipóteses investigadas, não24 afirmações factuais.
Separe número medido, hipótese causal, conclusão do autor e resultado próprio.
Pendência da nossa execução não significa inexistência de fonte.
Os comparadores históricosH07 e os totaisH13 de cadastro/Censo/comparecimento
já têm reprodução primária em resultados/. Confira-os na edição fixada.
Não confunda esses totais com identificação de óbitos. Preserve também o estado
técnico: reproduzido, divergente, parcialmente testável ou pendente.
Distinga fontes primárias, tabelas/capturas do autor e aritmética isolada.
H02 tem34.393 na tabela e34.424 após revisão textual: reconstituir o ajuste31.
Use analise/grade-validacao-r5.json como mapa de apresentação, não como prova.
Para a cronologia, leia também analise/atualizacao-temporal-r6.json.
Reproduza scripts/reconstruir_serie_temporal.py com o ZIP e manifesto fixados,
inclusive --targets para os primeiros dez/vinte minutos após19h. Confronte
fontes/observacoes-divulgacao.json usando scripts/confrontar_observacoes.py.
Confira os trechos nos localizadores de CNN/Band. Se transcrever as transmissões,
use segmentos com tempos para localizar Bahia e outras UFs; confirme números
no quadro e no documento. Não publique filmes nem transcrições integrais.
Separe hora da votação, encerramento, totalização, geração do JSON, captura,
relógio da TV, posição do player e publicação/atualização da notícia.
Calcule Δvotos/Δminutos e participação percentual separadamente. Preserve
lacunas, atraso, relógios contraditórios e cobertura regional assíncrona.
Não inferir contagem zero durante a pausa nem hora civil pelo começo da live.
Concordância entre emissoras pode repetir um mesmo feed. A curva por si só
não identifica votos dados nas duas horas extras nem o efeito da prorrogação.
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
