# Pacote de evidências para o Pergunte Aí

Estado: preparado para integração futura. Não houve ingestão, atualização de
fontes ativas, alteração de banco, prompt do atendente ou publicação de serviço.

## Entradas propostas

| Pacote leve | Uso analítico | Cuidado obrigatório |
|---|---|---|
| `resultados/idade.json` | Cadastro100+, Censo96+, comparecimento por idade | Fonte por turno; diferença agregada não identifica falecidos |
| `resultados/historico_secoes.json` | Zero voto e comparação2018/2022/2026 | Recorte Brasil/exterior; mesma chave não garante mesmos eleitores |
| `resultados/municipios.json` | Comparecimento/população, UF, abstenção e ganhos líquidos | Denominadores, aliases, edições distintas e inferência ecológica |
| `resultados/capturas.json` | Recalcular os números publicados e a série da noite | Camada derivada/preservada pelo autor, não reconstrução primária integral |
| `analise/grade-validacao-r5.json` | Navegar as24 hipóteses e a evidência disponível | Mapa de navegação; não fonte numérica autônoma |

Cada resposta deve carregar URL primária, SHA, edição, universo, fórmula e
resultado. A resposta também identifica se usou fonte primária, captura do
autor ou apenas uma identidade aritmética. Nunca promover um nível a outro.

## Perguntas de aceite

1. Quantos eleitores100+ e quantos comparecimentos existem no primeiro turno?
   Esperado297.977/2.141/0,72%; segundo turno deve reconhecer ausência do arquivo.
2. A diferença148.553 prova148.553 mortos? Mostrar a conta e distinguir a
   diferença entre bases do cruzamento de óbitos, inclusive datas/coortes.
3. Quantos municípios tiveram comparecimento maior que a população do Censo?
   Esperado120, Flávio venceu45; exibir cobertura5570/5571 e data2022 da população.
4. Os95,1% da Região dos Lagos significam95,1% dos votos? Não: calcular
   `28624/(28624+1476)` e chamar de participação no ganho líquido agregado.
5. Quais seis estados tiveram perda de votos do Flávio? AC/AM/AP/MA/RR/TO;
   informar a queda concomitante do comparecimento sem inventar causalidade.
6. O total nominal diminuiu nas346 versões nacionais? Zero reduções na série
   preservada; não prometer observação contínua dos intervalos.
7. São34.393 ou34.424 votos após17h? Expor as versões e o ajuste31 ainda não
   reconstruído por esta análise, sem misturar tabela e relatório final.

## Próximo ciclo do produto

O dono do Pergunte Aí resolve o catálogo, licenças, origem dos ZIPs, consultas
locais equivalentes, atualização por versão e testes de resposta. O artefato
leve pode servir de conjunto de avaliação e conhecimento metodológico; a
consulta numérica deve permanecer ligada às bases próprias validadas.
Não usar textos de roteiro como substitutos de tabelas de fatos.
