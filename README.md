# Finan

Educador financeiro com IA generativa para explicar conceitos de finanças pessoais de forma simples, segura e contextualizada.

O projeto utiliza dados fictícios para criar exemplos práticos. Seu objetivo é educar, não recomendar investimentos ou oferecer aconselhamento financeiro personalizado.

## O que foi desenvolvido

- Interface de conversa com Streamlit.
- Integração local com Ollama e o modelo `llama3.2:3b`.
- Leitura de dados estruturados em CSV e JSON.
- Cálculo determinístico de despesas por categoria com Pandas.
- Glossário controlado para conceitos financeiros recorrentes.
- Proteções contra recomendações específicas, exposição de dados confidenciais e tickers fora da base do projeto.
- Testes documentados para identificar limitações do modelo e validar as correções implementadas.

## Arquitetura resumida

```text
Usuário
   ↓
Streamlit
   ↓
Validações em Python
   ├── bloqueio de tickers fora do escopo
   └── cálculos determinísticos com Pandas
   ↓
Contexto + glossário + system prompt
   ↓
Ollama / llama3.2:3b
   ↓
Pós-processamento
   ↓
Resposta
```

A ideia central do projeto é não deixar responsabilidades críticas exclusivamente nas mãos do modelo. Cálculos e algumas validações são realizados diretamente pelo código, enquanto o LLM fica responsável principalmente pela interpretação e geração da resposta em linguagem natural.

## Estrutura do projeto

```text
data/       Dados fictícios do cliente, transações e produtos
docs/       Documentação, base de conhecimento, prompts, métricas e pitch
src/        Aplicação Streamlit
assets/     Recursos e materiais visuais/referências
```

## Como executar

1. Instale o [Ollama](https://ollama.com/) e baixe o modelo:

   ```bash
   ollama pull llama3.2:3b
   ```

2. Instale as dependências Python:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicie o Ollama e execute a aplicação:

   ```bash
   ollama serve
   streamlit run src/app.py
   ```

## Documentação

- [Documentação do agente](docs/01-documentacao-agente.md)
- [Base de conhecimento](docs/02-base-conhecimento.md)
- [Prompts e regras](docs/03-prompts.md)
- [Avaliação e métricas](docs/04-metricas.md)
- [Roteiro do pitch](docs/05-pitch.md)

## Limites do projeto

O Finan atua exclusivamente como ferramenta educacional. As informações geradas não substituem a análise de um profissional e não constituem recomendação de investimento.

O projeto utiliza dados fictícios e um modelo local. Ele foi construído como protótipo educacional e ainda possui limitações próprias de modelos de linguagem, que são documentadas na avaliação.

## Principais aprendizados

O desenvolvimento mostrou que um agente de IA não depende apenas de um bom prompt. A combinação de **LLM + regras determinísticas + dados estruturados + validações + testes** permite maior controle sobre o comportamento da aplicação e torna mais claros os limites do modelo.
