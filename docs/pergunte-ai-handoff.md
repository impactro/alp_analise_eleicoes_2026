# Pacote de evidências para o Pergunte Aí

Estado: preparado para integração futura. Não houve ingestão, atualização de
fontes ativas, alteração de banco, prompt do atendente ou publicação de serviço.

## Entradas propostas

| Pacote leve | Uso analítico | Cuidado obrigatório |
|---|---|---|
| `resultados/idade.json` | Cadastro 100+, Censo 96+, comparecimento por idade | Fonte por turno; diferença agregada não identifica falecidos |
| `resultados/historico_secoes.json` | Zero voto e comparação 2018/2022/2026 | Recorte Brasil/exterior; mesma chave não garante mesmos eleitores |
| `resultados/municipios.json` | Comparecimento/população, UF, abstenção e ganhos líquidos | Denominadores, aliases, edições distintas e inferência ecológica |
| `resultados/capturas.json` | Recalcular os números publicados e a série da noite | Camada derivada/preservada pelo autor, não reconstrução primária integral |
| `analise/grade-validacao-r5.json` | Navegar as 24 hipóteses e a evidência disponível | Mapa de navegação; não fonte numérica autônoma |
| `resultados/serie_temporal.json` | Âncoras, incrementos e cobertura de Brasil/regiões | Geração, captura e totalização separados; UFs assíncronas |
| `fontes/observacoes-divulgacao.json` e `resultados/confronto-divulgacao.json` | Conferir parciais de TV e imprensa | 16 quadros com relógio; concordância de exibição não é nova totalização |

Cada resposta deve carregar URL primária, SHA, edição, universo, fórmula e
resultado. A resposta também identifica se usou fonte primária, captura do
autor ou apenas uma identidade aritmética. Nunca promover um nível a outro.

## Perguntas de aceite

1. Quantos eleitores 100+ e quantos comparecimentos existem no primeiro turno?
   Esperado 297.977/2.141/0,72%; segundo turno deve reconhecer ausência do arquivo.
2. A diferença 148.553 prova 148.553 mortos? Mostrar a conta e distinguir a
   diferença entre bases do cruzamento de óbitos, inclusive datas/coortes.
3. Quantos municípios tiveram comparecimento maior que a população do Censo?
   Esperado 120, Flávio venceu 45; exibir cobertura 5570/5571 e data 2022 da população.
4. Os 95,1% da Região dos Lagos significam 95,1% dos votos? Não: calcular
   `28624/(28624+1476)` e chamar de participação no ganho líquido agregado.
5. Quais seis estados tiveram perda de votos do Flávio? AC/AM/AP/MA/RR/TO;
   informar a queda concomitante do comparecimento sem inventar causalidade.
6. O total nominal diminuiu nas 346 versões nacionais? Zero reduções na série
   preservada; não prometer observação contínua dos intervalos.
7. São 34.393 ou 34.424 votos após 17h? Expor as versões e o ajuste 31 ainda não
   reconstruído por esta análise, sem misturar tabela e relatório final.
8. Flávio perdeu votos entre 20h e 20h30? Os totais preservados crescem em
   18.977.434; a participação cai de 50,4685% para 49,7715%. Informar que são
   gerações 19:59:38 e 20:29:29, não horários individuais de votação.
9. O que a CNN mostrou às 19h22? Lula 1.783.016/Flávio 1.682.396, quadro
   `CNN-f11`, URL com localizador e versão 3959817. Relógio tem precisão de minuto.
10. Qual foi a velocidade durante a pausa? Reconhecer a lacuna 17:07:01→19:01:56;
    não preencher comzero ou chamar uma média entre pontas de curva observada.

## Próximo ciclo do produto

O dono do Pergunte Aí resolve o catálogo, licenças, origem dos ZIPs, consultas
locais equivalentes, atualização por versão e testes de resposta. O artefato
leve pode servir de conjunto de avaliação e conhecimento metodológico; a
consulta numérica deve permanecer ligada às bases próprias validadas.
Não usar textos de roteiro como substitutos de tabelas de fatos.
