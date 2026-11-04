# Proposta inicial — ALP: a conta está aberta

Data: 04/11/2026. Canal: YouTube/Crania-ia. Natureza: vídeo extra, por pedido
direto de Fábio, fora da agenda regular. Nenhuma pauta regular foi deslocada.

## Ideia e promessa

Abrir uma frente recorrente de investigação didática sobre dados brasileiros.
A CrânIA provoca a pergunta; AIstein explica os números. Cada episódio entrega
uma descoberta verificável e um repositório público pequeno para refazê-la.

Título de trabalho: **Eleitores mortos votaram? Vamos abrir a conta.**
Alternativa: **Eleições 2026: a conta fecha? Código aberto para conferir.**
O título final depende dos resultados; não anunciar fraude ou sua exclusão
antes da validação. Série proposta: **ALP — A conta está aberta**.

Público: pessoas interessadas em política, transparência e IA, sem exigir
Python. Formato: horizontal 16:9, Full HD. Duração planejada: 7 a 9 minutos,
respeitando o contrato vigente de 5 a 9 minutos dos longos da CrânIA.

## O primeiro episódio

O vídeo de Gabriel Carvalho tem 13:32 e discute 24 hipóteses. A descrição
aponta para seu projeto aberto. Vamos creditar essa origem e fazer uma
replicação independente, sem copiar sua narrativa, seus gráficos ou seu código.

O dossiê cobre as 24; o vídeo inicial concentra três perguntas:

1. **52,39% e o horário:** refazer os filtros por encerramento com e sem fuso;
   distinguir hora de encerramento, hora do voto e hora de recepção/divulgação.
2. **106 seções com zero voto:** contar o universo correto e comparar mesmas
   seções entre turnos e anos, indicando quantas puderam ser pareadas.
3. **Centenários e óbitos:** reproduzir os totais por idade, explicar a diferença
   entre cadastro, população residente e comparecimento, e delimitar o que não
   se pode concluir sem vínculo individual legalmente acessível.

O resultado nacional é controle prévio, não tese do episódio. Um primeiro
programa independente reproduziu, no arquivo oficial da geração 03/11/2026
19:31:38, a margem de 4.430.191 votos usada como referência no vídeo.

## Direção visual

- Abertura CrânIA: uma alegação viral e a pergunta concreta; sem montagem
  acusatória ou pessoas retratadas como culpadas.
- Traço Robótico: construir três caixas — fonte, programa, resultado — e
  revelar os números conforme a explicação. Desenho é explicação, não evidência.
- Lousa progressiva: dois relógios e a mesma seção para o fuso; denominador e
  filtros aparecem junto do resultado. Fuso do oeste do Amazonas exige mapa
  municipal, não um deslocamento único para toda a UF.
- Mapa e barras: seções de votação, com contagem/recorte/ano explícitos; não
  usar escala que transforme uma pequena diferença em efeito visual enorme.
- Lousa dos centenários: cadastro, Censo e comparecimento em colunas distintas;
  uma seta interrompida mostra por que diferença agregada não identifica óbito.
- Fechamento: resumo dos resultados efetivamente reproduzidos e como refazer
  a análise. Quadros de código apenas quando legíveis e úteis ao público.

Não há quota de recursos ou obrigação de personagem em todos os planos.
CDraw prepara assets; CPlay coordena; CAudio produz áudio; CVideo anima e monta.
Lousa e Traço dependem de preflight das operações exatas e QA visual Sol 6.1
antes da produção. Esta proposta não declara tais cenas já executadas.

## IA e divulgação dos trabalhos de Fábio

Depois da primeira conta demonstrada, inserir uma ponte de cerca de 20–30s:
Fábio desenvolve sistemas e agentes de IA para organizar informações e apoiar
trabalho real. O Pergunte Aí permite explorar dados em linguagem comum; o GitHub
expõe o procedimento para conferência. Não prometer ausência de erros,
atualização contínua universal, resultado comercial ou capacidade não testada.

CTA final: experimentar uma pergunta, abrir as fontes e propor uma reprodução.
Mentoria pode ser citada como caminho para aprender a aplicar o método ao
próprio trabalho, sem preço ou oferta no roteiro inicial.

### Fechamento dirigido por Fábio — 04/11/2026

Depois dos resultados, apresentar um prompt curto para reproduzir a análise e
o endereço `github.com/impactro/alp_analise_eleicoes_2026`. O
[prompt integral](prompt-reproducao.md) fica disponível no repositório e é
referenciado na descrição. Depois, agradecer Gabriel Carvalho pela ideia,
estudo e narrativa, com pequenas cenas creditadas do vídeo original. O plano
do roteiro propõe três excertos de cerca de dois segundos; os cortes reais
dependem da inspeção do material na produção.

Encerrar com a direção autoral: “Juntos, com inteligência natural, podemos
vencer a burrice artificial implantada na humanidade. Porque só o conhecimento
liberta. Compartilhe e siga para muito mais!”

Meta ajustada do roteiro estrutural: cerca de 8min35s, sujeita à narração
medida e ao teto de nove minutos. Créditos e links aparecem com tempo de leitura;
nenhum trecho ou áudio foi renderizado por esta atualização editorial.

Referências editoriais, reutilizadas por pedido explícito de Fábio:

- Conhecimento-Liberta, `2026-10-07-A-panorama-pergunte-ai`: ponte entre dados
  públicos, perguntas empresariais e ensino; estado do roteiro não prova vídeo
  publicado.
- Conhecimento-Liberta, `2026-10-02-A-ces-arquitetura`: explicar sistemas a partir
  de resultados, componentes e manutenção. Números comerciais de depoimentos
  antigos não serão reaproveitados como situação atual.

Preservar identidade e autorização da CrânIA; essas referências não transferem
credenciais, agenda ou permissões do Conhecimento Liberta.

## Projeto público e área do canal

Repositório: `impactro/alp_analise_eleicoes_2026`. Primeira entrega contém
proposta, matriz, fontes, método e controle nacional reproduzível.
Meta inicial: menos de 5 MiB de arquivos rastreados, limite revisável por
necessidade real. Vídeos e originais nunca entram no histórico Git.

Área `ALP/` do canal guarda organização editorial, extração de referência e
evidências de trabalho não destinadas ao GitHub. Código canônico vive no
repositório próprio; apontar para uma revisão pública evita duas cópias editáveis.

## Etapas e aceite

1. **Descoberta inicial:** transcrição, projeto original fixado por commit,
   matriz de alegações, inventário de fontes e controle nacional. Esta rodada.
2. **Replicação:** implementar cada cálculo em código próprio; executar sobre
   a mesma edição e uma edição atual separada; comparar resultados e limites.
3. **Revisão analítica independente:** conferir dados, denominadores, chaves,
   inferências e evidências. Conferência própria não recebe esse rótulo.
4. **Roteiro final:** substituir hipóteses por resultados validados; vincular
   cada número a saída/consulta/commit; ajustar duração pelo conteúdo.
5. **Prévia visual e produção:** prévia barata dos trechos difíceis, áudio,
   cenas, master, QA e fechamento. Publicação do vídeo fica para pedido próprio.

Um cálculo passa quando outra execução, a partir de fontes públicas e versão
registrada, reproduz a saída dentro de tolerância declarada. Uma alegação pode
ser numericamente reproduzida e ter interpretação não demonstrada. Falta de
dado não vira zero nem confirmação de hipótese.

## Evolução para o ALP

Propor ao mantenedor, sem modificar o atendimento nesta rodada:
perfil/comparecimento por idade e turno; boletins e detalhe por seção;
geografia e população por data de referência; séries históricas de totalização
com proveniência; glossário de campos e advertências metodológicas.

Cada coleção deve ter fonte pública, licença, granularidade, chaves, atualização,
manifesto, testes, cobertura e operações somente leitura próprias. Não importar
os vereditos deste vídeo como fatos aprendidos pelo agente. Web e WhatsApp
mantêm suas seleções de acesso explícitas.

Depois: despesas públicas, emendas, contratos e indicadores brasileiros, cada
análise com pergunta delimitada e repositório `alp_<nome_da_analise>`.
