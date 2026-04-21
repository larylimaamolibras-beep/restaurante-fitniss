import streamlit as st
from datetime import datetime

# 1. Configuração da Página e Remoção de Rodapés (Tudo aqui no topo!)
st.set_page_config(page_title="Restaurante Fitness", layout="wide")

# Esse bloco de CSS abaixo remove o e-mail (se houvesse), o menu e o "Made with Streamlit"
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. BANCO DE DADOS COMPARTILHADO
@st.cache_resource
def iniciar_banco_dados():
    return {"pedidos": [], "caixa": 0.0}

dados_globais = iniciar_banco_dados()

# 3. Tabela de Preços
PRECOS = {
    "Frango Grelhado": 8.00, "Salada Prime": 5.00, "Suco Detox": 12.00,
    "Omelete Proteico": 5.00, "Bowl de Açaí Fit": 10.00, "Peixe com Quinoa": 25.00,
    "Café Expresso Fit": 5.50, "Sanduíche Integral": 10.00, "Sopa de Legumes": 10.00,
    "Tapioca Fit": 5.00
}

# 4. Estilo Visual Adicional
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1490818387583-1baba5e638af?q=80&w=2000&auto=format&fit=crop");
        background-attachment: fixed; background-size: cover;
    }
    .topo-fixo {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #1b5e20 !important; color: white !important;
        text-align: center; padding: 15px 0px; font-size: 30px; font-weight: bold; z-index: 9999;
    }
    .stMainBlockContainer {
        background-color: rgba(255, 255, 255, 0.9) !important; 
        padding-top: 20px !important; border-radius: 0px 0px 20px 20px; margin-top: 75px !important;
    }
    [data-testid="stColumn"] { display: flex !important; flex-direction: column !important; align-items: center !important; text-align: center !important; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; width: 180px !important; border-radius: 8px !important; }
    
    .status-cozinha { color: #FF8C00 !important; font-weight: bold; } 
    .status-pagamento { color: #FF0000 !important; font-weight: bold; } 
    .status-ok { color: #008000 !important; font-weight: bold; } 
    
    .caixa-total { 
        background-color: #1b5e20; color: white !important; padding: 20px; 
        border-radius: 10px; text-align: center; font-size: 26px; border: 3px solid #FFD700;
    }
    h1, h2, h3, p, label, span { color: #000000 !important; font-weight: bold !important; }
    </style>
    <div class="topo-fixo">🥗 Restaurante Fitness</div>
    """, unsafe_allow_html=True)

# 5. Sacola Local
if 'sacola' not in st.session_state:
    st.session_state.sacola = []

def criar_item(coluna, nome, foto):
    with coluna:
        try:
            st.image(foto, width=150)
            st.markdown(f"**{nome}**")
            st.markdown(f"**R$ {PRECOS[nome]:.2f}**")
            if st.button(f"🛒 Adicionar", key=f"btn_{nome}"):
                st.session_state.sacola.append({"nome": nome, "preco": PRECOS[nome]})
                st.toast(f"{nome} adicionado!")
        except: st.error(f"Erro na foto {nome}")

# --- CARDÁPIO ---
c1, c2 = st.columns(2); criar_item(c1, "Frango Grelhado", "frango.jpg"); criar_item(c2, "Salada Prime", "salada.jpg")
c3, c4 = st.columns(2); criar_item(c3, "Suco Detox", "suco.jpg"); criar_item(c4, "Omelete Proteico", "omelete.jpg")
c5, c6 = st.columns(2); criar_item(c5, "Bowl de Açaí Fit", "acai.jpg"); criar_item(c6, "Peixe com Quinoa", "peixe.jpg")
c7, c8 = st.columns(2); criar_item(c7, "Café Expresso Fit", "cafe.jpg"); criar_item(c8, "Sanduíche Integral", "sanduiche.jpg")
c9, c10 = st.columns(2); criar_item(c9, "Sopa de Legumes", "sopa.jpg"); criar_item(c10, "Tapioca Fit", "tapioca.jpg")

st.divider()

# --- ÁREA DO CLIENTE ---
st.subheader("🛒 Seu Carrinho")
if st.session_state.sacola:
    for item in st.session_state.sacola:
        st.write(f"✅ {item['nome']} - R$ {item['preco']:.2f}")
    
    nome_c = st.text_input("Seu Nome:")
    mesa_c = st.number_input("Mesa:", min_value=1, step=1)
    
    if st.button("🚀 ENVIAR PEDIDO COMPLETO"):
        if nome_c:
            novo_p = {
                "ID": len(dados_globais["pedidos"]) + 1,
                "Hora": datetime.now().strftime("%H:%M"),
                "Mesa": mesa_c,
                "Cliente": nome_c,
                "Itens": ", ".join([x['nome'] for x in st.session_state.sacola]),
                "Total": sum([x['preco'] for x in st.session_state.sacola]),
                "Status": "Cozinha"
            }
            dados_globais["pedidos"].append(novo_p)
            st.session_state.sacola = []
            st.success("Pedido enviado! Olhe o computador agora.")
            st.rerun()
else:
    st.info("Adicione itens acima.")

# --- PAINEL ADM ---
st.divider()
st.subheader("📟 Gestão (Visível em todos os aparelhos)")

if dados_globais["pedidos"]:
    for i, p in enumerate(dados_globais["pedidos"]):
        with st.expander(f"Mesa {p['Mesa']} - {p['Cliente']}"):
            st.write(f"**Pedido:** {p['Itens']}")
            
            if p['Status'] == "Cozinha":
                st.markdown(f"Status: <span class='status-cozinha'>🟠 AGUARDANDO ENTREGA</span>", unsafe_allow_html=True)
                if st.button(f"Entregue na Mesa #{p['ID']}", key=f"ent_{i}"):
                    dados_globais["pedidos"][i]["Status"] = "Pagamento"
                    st.rerun()
            
            elif p['Status'] == "Pagamento":
                st.markdown(f"Status: <span class='status-pagamento'>🔴 AGUARDANDO PAGAMENTO</span>", unsafe_allow_html=True)
                if st.button(f"PAGAMENTO REALIZADO #{p['ID']}", key=f"pay_{i}"):
                    dados_globais["pedidos"][i]["Status"] = "Finalizado"
                    dados_globais["caixa"] += p['Total']
                    st.rerun()
            else:
                st.markdown(f"Status: <span class='status-ok'>🟢 PAGO</span>", unsafe_allow_html=True)

st.markdown(f'<div class="caixa-total">💰 CAIXA TOTAL: R$ {dados_globais["caixa"]:.2f}</div>', unsafe_allow_html=True)

if st.button("🧹 Zerar Tudo"):
    dados_globais["pedidos"] = []
    dados_globais["caixa"] = 0.0
    st.rerun()