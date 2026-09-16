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

# ============ SYSTEM PROMPT (simplificado) ============
SYSTEM_PROMPT = """Você é o Finan, educador financeiro amigável e didático.

OBJETIVO: ensinar finanças pessoais de forma simples, usando os dados do cliente para exemplos práticos.

REGRAS:
1. Nunca recomende um investimento, ativo ou produto específico. Apenas explique como funcionam.
2. Não dê aconselhamento financeiro personalizado. Seu papel é só educacional.
3. Use os dados do cliente para exemplos práticos, nunca como recomendação.
4. Fale de forma simples e amigável, como se explicasse para um amigo iniciante.
5. Se usar termo técnico, explique o significado de forma simples.
6. Nunca invente dado, valor, taxa, período de tempo ou característica de ativo/empresa que não esteja no CONTEXTO ou nas DEFINIÇÕES fornecidas. Se não souber, diga: "Não tenho essa informação, mas posso explicar o conceito."
7. Se a pergunta for fora de educação financeira pessoal, responda: "Sou o Finan, seu educador financeiro, e posso ajudar apenas com assuntos relacionados à educação financeira pessoal."
8. Nunca julgue ou critique a situação financeira do cliente.
9. Em cálculos, mostre a lógica de forma simples antes do resultado.
10. Termine perguntando se o cliente entendeu ou quer um exemplo, quando fizer sentido.
11. Responda só o que foi perguntado. Não puxe um assunto novo sozinho.
12. Nunca peça, dê ou repita senha, dado bancário, número de cartão ou outro dado confidencial de qualquer cliente.
"""

# ============ GLOSSÁRIO DE TERMOS (evita explicação errada de conceito pelo modelo) ============
GLOSSARIO = {
    "selic": "Selic é a taxa básica de juros da economia brasileira, definida periodicamente pelo Copom (Banco Central). Ela serve de referência para todas as outras taxas de juros do país.",
    "cdi": "CDI (Certificado de Depósito Interbancário) é uma taxa de juros usada como referência para investimentos de renda fixa, e costuma ficar bem próxima da Selic.",
    "tesouro selic": "Tesouro Selic é um título público (você empresta dinheiro para o governo) cuja rentabilidade acompanha a taxa Selic. É considerado de baixo risco e tem alta liquidez (dá para resgatar rapidamente).",
    "cdb": "CDB (Certificado de Depósito Bancário) é um título emitido por bancos, no qual o investidor empresta dinheiro ao banco e recebe de volta com juros, geralmente em % do CDI.",
    "lci": "LCI (Letra de Crédito Imobiliário) é um título emitido por bancos, isento de Imposto de Renda para pessoa física, com o dinheiro captado destinado ao setor imobiliário.",
    "lca": "LCA (Letra de Crédito do Agronegócio) é um título emitido por bancos, isento de Imposto de Renda para pessoa física, com o dinheiro captado destinado ao agronegócio.",
    "fii": "FII (Fundo de Investimento Imobiliário) é um fundo que investe em imóveis ou títulos ligados ao setor imobiliário, distribuindo parte dos rendimentos aos cotistas periodicamente.",
    "renda fixa": "Renda fixa é uma categoria de investimento em que as regras de rentabilidade são definidas no momento da aplicação (uma taxa fixa ou atrelada a um índice), geralmente com risco mais baixo.",
    "renda variável": "Renda variável é uma categoria de investimento cuja rentabilidade não é conhecida previamente e pode variar de acordo com o mercado (ex: ações), geralmente com risco mais alto.",
    "reserva de emergência": "Reserva de emergência é uma quantia guardada para cobrir despesas inesperadas, geralmente equivalente a 3 a 6 meses de gastos, mantida em investimentos de baixo risco e fácil resgate.",
}

def buscar_definicoes(msg):
    """Retorna as definições do glossário cujos termos aparecem na pergunta,
    para o modelo usar como base em vez de explicar o conceito de memória própria."""
    msg_lower = msg.lower()
    encontrados = [defin for termo, defin in GLOSSARIO.items() if termo in msg_lower]
    if not encontrados:
        return ""
    return "DEFINIÇÕES VALIDADAS (use estas ao explicar, não crie definição própria):\n" + "\n".join(f"- {d}" for d in encontrados)

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

    definicoes = buscar_definicoes(msg)

    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    {definicoes}

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
