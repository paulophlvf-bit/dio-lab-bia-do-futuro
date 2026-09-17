# Passo a Passo de Execução

## Setup do Ollama

```bash
# 1. Instalar Ollama (ollama.com)
# 2. Baixar um modelo leve
ollama pull llama3.2:3b

# 3. Testar se funciona
ollama run llama3.2:3b "Olá!"
```

## Código Completo

Todo o código-fonte está no arquivo `app.py`.

## Como Rodar

```bash
# 1. Instalar dependências
pip install streamlit pandas requests

# 2. Garantir que Ollama está rodando
ollama serve

# 3. Rodar o app
streamlit run .\src\app.py
```

## Evidência de Execução

<img width="1098" height="848" alt="image" src="https://github.com/user-attachments/assets/4cb70db7-8835-4fd4-86f1-037680f2dc62" />
