# Base de Conhecimento

A base de conhecimento do agente **Finan** reúne os dados utilizados para contextualizar as respostas do modelo. Ela é formada pelos arquivos da pasta `data/` e é carregada pela aplicação em Python.

## Dados Utilizados

| Arquivo | Formato | Para que serve no Finan? |
|---------|---------|---------------------------|
| `historico_atendimento.csv` | CSV | Fornece o histórico de interações anteriores do cliente. |
| `perfil_investidor.json` | JSON | Contém os dados de perfil, objetivos, patrimônio e metas utilizados como contexto. |
| `produtos_financeiros.json` | JSON | Contém os produtos financeiros disponíveis para explicação pelo agente. |
| `transacoes.csv` | CSV | Contém as transações usadas para gerar o resumo de gastos por categoria. |

---

## Adaptações nos Dados

O produto **Fundo Imobiliário (FII)** substituiu o Fundo Multimercado, pois pessoalmente me sinto mais confiante em usar produtos financeiros que conheço. Assim, posso validar as respostas do Finan com mais segurança durante os testes.

---

## Estratégia de Integração

### Como os dados são carregados?

Os arquivos são carregados diretamente pela aplicação em `src/app.py`:

```python
import json
import pandas as pd

perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))
```

Além de carregar as transações, a aplicação calcula automaticamente os totais das despesas por categoria:

```python
totais_por_categoria = transacoes[transacoes['tipo'] == 'saida'].groupby('categoria')['valor'].sum().round(2)
resumo_totais = "\n".join([f"- {cat}: R$ {valor:.2f}" for cat, valor in totais_por_categoria.items()])
```

Dessa forma, o contexto utilizado pelo Finan é montado a partir dos dados reais presentes nos arquivos da aplicação, em vez de depender apenas de um texto estático copiado manualmente.

### Como os dados são usados no prompt?

Os dados são incorporados ao contexto enviado ao modelo junto com as instruções do **system prompt**. O contexto inclui:

- perfil e objetivos do cliente;
- patrimônio e reserva de emergência;
- transações registradas;
- totais de gastos calculados por categoria;
- histórico de atendimento;
- produtos financeiros disponíveis para explicação.

O Finan também possui um pequeno glossário de conceitos financeiros validados no próprio código. Quando uma pergunta contém termos como **Selic, CDI, Tesouro Selic, CDB, LCI, LCA, FII, renda fixa, renda variável** ou **reserva de emergência**, a aplicação adiciona as definições correspondentes ao contexto antes de consultar o modelo.

---

## Exemplo de Contexto Montado

O contexto enviado ao modelo pode ser sintetizado para destacar as informações mais relevantes:

```text
DADOS DO CLIENTE:
- Nome: João Silva
- Perfil: Moderado
- Objetivo: Construir reserva de emergência
- Renda mensal: R$ 5.000,00
- Patrimônio total: R$ 15.000,00
- Reserva de emergência atual: R$ 10.000,00
- Meta da reserva: R$ 15.000,00

RESUMO DE GASTOS:
- Moradia: R$ 1.380,00
- Alimentação: R$ 570,00
- Transporte: R$ 295,00
- Saúde: R$ 487,90
- Lazer: R$ 55,90
- Total de saídas: R$ 2.788,80

PRODUTOS DISPONÍVEIS PARA EXPLICAR:
- Tesouro Selic (risco baixo)
- CDB Liquidez Diária (risco baixo)
- LCI/LCA (risco baixo)
- Fundo Imobiliário - FII (risco médio)
- Fundo de Ações (risco alto)
```

Os valores do resumo são calculados a partir de `data/transacoes.csv`. Por isso, se os dados da base forem alterados, os totais calculados pela aplicação também podem mudar.

---

## Cuidados no Uso da Base

A base de conhecimento serve para **contextualizar e ensinar**, não para transformar o Finan em um consultor de investimentos. O `system prompt` determina que o agente não deve recomendar investimentos, ativos ou produtos financeiros específicos, nem inventar informações que não estejam disponíveis no contexto ou nas definições utilizadas.

Também existe uma proteção determinística para perguntas que contenham padrões de ticker, evitando que o modelo invente informações sobre ativos que não fazem parte dos produtos disponíveis para ensino.
