import json
import re
import streamlit as st
import pandas as pd
import requests

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate" 
MODELO = "llama3.2:3b"

# ============ CARREGAR DADOS ============
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ============ CALCULAR TOTAIS (evita erro de soma do modelo) ============
totais_por_categoria = transacoes[transacoes['tipo'] == 'saida'].groupby('categoria')['valor'].sum().round(2)
resumo_totais = "\n".join([f"- {cat}: R$ {valor:.2f}" for cat, valor in totais_por_categoria.items()])

# ============ MONTAR CONTEXTO ============
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES (detalhado):
{transacoes.to_string(index=False)}

TOTAIS JÁ CALCULADOS POR CATEGORIA (use estes valores prontos, não recalcule):
{resumo_totais}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """Você é o Finan, um educador financeiro amigável, didático e acessível.

OBJETIVO:
Ensinar conceitos de finanças pessoais de maneira simples, clara e prática, utilizando os dados fornecidos pelo usuário para criar exemplos personalizados e facilitar o aprendizado.

1. Não recomende investimentos específicos, ativos, produtos financeiros, corretoras ou estratégias personalizadas de investimento. Explique apenas como funcionam, seus conceitos, características, riscos e diferenças.
2. Não forneça aconselhamento financeiro personalizado. Seu papel é exclusivamente educacional.
3. Utilize os dados fornecidos pelo usuário para criar exemplos práticos e personalizados**, sem apresentar esses exemplos como recomendações.
4. Use uma linguagem simples, natural e amigável, como se estivesse explicando o assunto para um amigo que está começando a aprender.
5. Evite termos técnicos desnecessários. Quando um termo técnico for importante, explique seu significado de forma simples.
6. Nunca invente informações, valores, taxas ou dados. Quando não souber algo, diga: "Não tenho essa informação, mas posso explicar o conceito." Isso inclui NUNCA descrever características, empresas, setores ou detalhes de ativos, tickers, fundos ou instituições específicas que não estejam listados em PRODUTOS DISPONÍVEIS — mesmo que você "ache" que sabe do que se trata. Nesses casos, diga apenas que não tem essa informação e ofereça explicar o conceito geral (ex: o que é uma ação, o que é um ticker). Também nunca invente um período de tempo (ex: "nos últimos 30 dias", "no último mês") que não esteja explicitamente presente nos dados — se as transações não tiverem datas relativas ao momento atual, não presuma um intervalo de tempo.
7. Se o usuário fizer uma pergunta fora do tema de educação financeira pessoal, responda: "Sou o Finan, seu educador financeiro, e posso ajudar apenas com assuntos relacionados à educação financeira pessoal."
8. Não julgue ou critique a situação financeira do usuário. Seja sempre respeitoso, paciente e incentivador.
9. Quando houver cálculos, apresente a lógica de forma simples e mostre o resultado de maneira clara.
10. Ao final da explicação, pergunte se o usuário entendeu ou se deseja um exemplo prático, sempre que isso fizer sentido.
11. Seja sucinto e direto, com no máximo 3 parágrafos, salvo quando uma explicação, cálculo ou lista exigir uma estrutura diferente para ficar clara. Responda apenas o que foi perguntado: não inicie um novo tópico financeiro (ex: reserva de emergência, investimentos) por conta própria se o usuário não pediu isso. Você pode perguntar ao final se o usuário quer explorar outro assunto, mas não desenvolva esse assunto sem ele confirmar.
12. Nunca peça, forneça ou compartilhe senhas, códigos de segurança, dados bancários, números de cartão, documentos, tokens ou outras informações confidenciais de clientes. Esses dados devem permanecer protegidos e não devem ser expostos ou repetidos pelo agente. Para exemplos ou demonstrações, utilize sempre informações fictícias ou dados mascarados.
"""

# ============ DETECÇÃO DE TICKERS FORA DO ESCOPO ============
# Tickers da B3 seguem o padrão: 4 letras + 1 ou 2 dígitos (ex: BBDC3, PETR4, VALE3, ITUB4, HGLG11)
PADRAO_TICKER = re.compile(r'\b[A-Za-z]{4}\d{1,2}\b')
RESPOSTA_PADRAO_TICKER = (
    "Não tenho essa informação, mas posso explicar o conceito. "
    "Não trabalho com dados de ativos específicos da bolsa (como cotações ou rendimentos de ações "
    "individuais) — meu papel é te ajudar a entender como esses instrumentos funcionam de forma geral. "
    "Quer que eu explique o que é uma ação, um ticker, ou como funciona o mercado de ações?"
)

def contem_ticker_fora_do_escopo(msg):
    """Detecta se a pergunta menciona um ticker (padrão B3) que não está nos produtos disponíveis."""
    candidatos = PADRAO_TICKER.findall(msg)
    if not candidatos:
        return False
    nomes_produtos = " ".join(p['nome'].upper() for p in produtos)
    for candidato in candidatos:
        if candidato.upper() not in nomes_produtos:
            return True
    return False

# ============ DETECÇÃO DE CONSULTA OBJETIVA DE DADO ============
# Perguntas assim (ex: "quanto gastei com X?") esperam só o dado, não um novo assunto emendado.
PALAVRAS_CONSULTA_OBJETIVA = ["quanto", "qual foi", "qual é", "quantos", "quantas"]

def eh_consulta_objetiva(msg):
    msg_lower = msg.lower()
    return any(p in msg_lower for p in PALAVRAS_CONSULTA_OBJETIVA)

def podar_resposta(resposta):
    """Mantém só o primeiro parágrafo (a resposta ao que foi perguntado) e garante
    que termine com uma pergunta de fechamento, cortando qualquer novo assunto
    que o modelo tenha emendado sozinho."""
    paragrafos = [p.strip() for p in resposta.split("\n") if p.strip()]
    if not paragrafos:
        return resposta
    primeiro = paragrafos[0]
    # Se o primeiro "parágrafo" for só uma saudação curta (ex: "Olá João! Vamos lá!"),
    # inclui também o segundo, que costuma ter o dado de fato.
    if len(primeiro) < 40 and len(paragrafos) > 1:
        primeiro = primeiro + " " + paragrafos[1]
    if not primeiro.rstrip().endswith("?"):
        primeiro += " Quer que eu explique melhor ou veja outro dado?"
    return primeiro

# ============ CHAMAR OLLAMA ============
def perguntar(msg):
    # Intercepta perguntas sobre tickers específicos antes de chamar o modelo,
    # evitando que ele "invente" características de ativos que não conhece de verdade.
    if contem_ticker_fora_do_escopo(msg):
        return RESPOSTA_PADRAO_TICKER

    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    r = requests.post(OLLAMA_URL, json={
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "seed": 42
        }
    })
    resposta = r.json()['response']
    # Se a pergunta era uma consulta objetiva de dado, poda qualquer novo assunto
    # que o modelo tenha emendado sozinho (viola a regra 11).
    if eh_consulta_objetiva(msg):
        resposta = podar_resposta(resposta)
    # Escapa o "$" para o Streamlit não interpretar como delimitador de LaTeX/matemática,
    # o que causava a corrupção visual tipo "R`" no lugar de "R$"
    return resposta.replace("$", "\\$")

# ============ INTERFACE ============
st.title("🎓 Finan, o Educador Financeiro")

if pergunta := st.chat_input("Sua dúvida sobre finanças...", key="finan_chat_input"):
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):
        st.chat_message("assistant").write(perguntar(pergunta))
