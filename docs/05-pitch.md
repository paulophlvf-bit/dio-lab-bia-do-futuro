# Pitch — Finan

**Duração aproximada: 2min55s**

## Slide 1 — Título — 0:00 a 0:10

> "Esse é o Finan, um educador financeiro desenvolvido com inteligência artificial. A ideia é simples: ajudar quem está começando a entender finanças, sem transformar o agente em alguém que recomenda investimentos."

## Slide 2 — O problema — 0:10 a 0:28

> "Quando uma pessoa começa a estudar finanças, ela encontra muitos termos que parecem complicados, como CDB, CDI, renda fixa e renda variável. E também pode encontrar conteúdos que misturam educação com indicação de produtos. Então eu quis criar uma solução focada primeiro em explicar e ensinar."

## Slide 3 — O agente — 0:28 a 0:46

> "O Finan roda localmente, usando Streamlit, Ollama e um modelo de linguagem. Ele também utiliza uma base com perfil, transações e histórico de um cliente fictício, permitindo criar exemplos mais próximos da realidade. Mas existe uma regra importante: o agente pode explicar um investimento, mas não deve dizer qual investimento a pessoa deve escolher."

## Slide 4 — O agente funcionando — 0:46 a 1:08

> "Aqui eu mostro o Finan funcionando. Quando faço uma pergunta sobre um ativo específico que não está na base de conhecimento, ele não precisa simplesmente tentar adivinhar uma resposta. Existe uma validação no código que identifica esse tipo de consulta antes de ela chegar ao modelo. Assim, o agente reconhece o limite das informações disponíveis e direciona a resposta para o que ele realmente pode explicar."

## Slide 5 — O que eu encontrei nos testes — 1:08 a 1:28

> "E essa parte foi uma das mais importantes do desenvolvimento. Nos primeiros testes, encontrei alguns problemas: o modelo podia errar cálculos simples, inventar informações que não estavam na base e, em alguns casos, até ultrapassar a regra de não recomendar produtos. Foi aí que percebi que simplesmente melhorar o prompt não seria suficiente."

## Slide 6 — Prompt não resolve tudo — 1:28 a 1:48

> "O prompt continua sendo importante, mas ele não pode ser a única camada de proteção. Um modelo de linguagem pode interpretar uma instrução de forma diferente dependendo da pergunta. Então eu comecei a tirar do modelo algumas responsabilidades que poderiam ser resolvidas de uma maneira mais previsível pelo próprio código."

## Slide 7 — As correções — 1:48 a 2:08

> "Por exemplo, os cálculos de gastos passaram a ser feitos diretamente em Python com Pandas. Consultas sobre ativos fora do escopo são identificadas antes de chegar à IA. E eu também criei um glossário controlado para alguns termos financeiros, fornecendo ao modelo definições que já foram preparadas para o projeto."

## Slide 8 — O principal aprendizado — 2:08 a 2:26

> "Para mim, esse foi o principal diferencial do projeto. Eu percebi que construir um agente de IA não é apenas escolher um modelo e escrever um bom prompt. É preciso entender as limitações do modelo e combinar a inteligência artificial com regras, dados e código para tornar o comportamento mais previsível."

## Slide 9 — Resultados — 2:26 a 2:40

> "Depois dessas mudanças, os testes mostraram uma melhora importante no comportamento do agente. Os cálculos passaram a ser feitos de forma determinística, as consultas fora da base passaram a ser filtradas e as regras de comportamento ficaram documentadas e testáveis."

## Slide 10 — Fechamento — 2:40 a 2:55

> "No final, o maior aprendizado para mim foi entender que desenvolver uma aplicação com IA vai muito além de fazer o modelo responder perguntas. É saber onde ele pode errar e construir mecanismos para reduzir esses erros. E esse foi o principal objetivo do Finan."

---

## Objetivo do pitch

Apresentar de forma rápida e prática o problema, a arquitetura, as proteções, os testes e os principais aprendizados obtidos durante o desenvolvimento do Finan.

## Tecnologias destacadas

- Python
- Streamlit
- Ollama
- Modelo de linguagem local
- Pandas
- CSV e JSON
- Regras de validação
- Glossário controlado

## Checklist do Pitch

- [x] Duração abaixo de 3 minutos
- [x] Problema definido
- [x] Solução apresentada
- [x] Demonstração do agente prevista
- [x] Diferenciais técnicos explicados
- [x] Aprendizados e resultados apresentados

## Link do vídeo

> Adicione aqui o link do pitch após a gravação.

[Link do vídeo]
