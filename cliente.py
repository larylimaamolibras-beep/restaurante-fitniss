import streamlit as st
import json
import os
import time
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Cardápio Restaurante Fitness", layout="centered")

DB_FILE = "banco_dados.json"

def carregar_dados():
    if not os.path.exists(DB_FILE): 
        return {"cardapio": [], "pedidos": []}
    try:
        with open(DB_FILE, "r", encoding='utf-8') as f: 
            return json.load(f)
    except:
        return {"cardapio": [], "pedidos": []}

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding='utf-8') as f: 
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- SEU ESTILO ORIGINAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, .stMarkdown { color: white !important; }
    
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #333; }
    [data-testid="stSidebar"] label { color: #FFFFFF !important; font-weight: bold; }

    .secao-titulo { 
        background-color: #00FF00; color: black !important; 
        padding: 10px; border-radius: 10px; text-align: center; 
        font-weight: 900; margin: 20px 0;
    }
    
    .item-container { 
        border: 2px solid #00FF00; padding: 15px; 
        border-radius: 15px; margin-bottom: 20px; background: #111; 
    }
    
    div.stButton > button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        transition: none !important;
    }
    div.stButton > button:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

dados = carregar_dados()

# CONSERTO 1: Key única para a mesa (Resolve erro da imagem e264d0)
mesa_selecionada = st.sidebar.selectbox(
    "📍 Selecione sua Mesa:", 
    [f"Mesa {i:02d}" for i in range(1, 21)], 
    key="selectbox_mesa_unica"
)

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("🍏 RESTAURANTE FITNESS")

# --- SEÇÃO DE PRATOS ---
st.markdown('<div class="secao-titulo">🍲 MONTE SEU PRATO</div>', unsafe_allow_html=True)
pratos = [x for x in dados.get('cardapio', []) if x.get('tipo') == "Prato"]

for i, item in enumerate(pratos):
    p_orig = item.get('preco', 0.0)
    em_promo = item.get('em_promo', False)
    porcentagem = item.get('porcentagem', 0)
    p_final = p_orig * (1 - (porcentagem / 100)) if em_promo else p_orig

    with st.container():
        st.markdown('<div class="item-container">', unsafe_allow_html=True)
        col_img, col_info = st.columns([1, 1.5])
        with col_img:
            if item.get('imagem'): st.image(item['imagem'], use_container_width=True)
        with col_info:
            st.subheader(item['item'])
            if em_promo:
                st.error(f"PROMOÇÃO -{porcentagem}%")
                st.write(f"~~R$ {p_orig:.2f}~~")
                st.success(f"R$ {p_final:.2f}")
            else:
                st.write(f"**Valor: R$ {p_orig:.2f}**")
            
        st.write("**O que vai no prato?**")
        c1, c2, c3 = st.columns(3)
        tem_arroz = c1.checkbox("Arroz", value=True, key=f"ar_p_{i}")
        tem_feijao = c2.checkbox("Feijão", value=True, key=f"fe_p_{i}")
        tem_mac = c3.checkbox("Macarrão", value=True, key=f"ma_p_{i}")
        
        carne = st.radio("Escolha sua Proteína:", ["Frango", "Carne de Sol", "Omelete","Fígado", "Peixe"], key=f"prot_p_{i}")
        
        if st.button(f"🛒 Adicionar Prato", key=f"btn_p_p_{i}"):
            escolhas = []
            if tem_arroz: escolhas.append("Arroz")
            if tem_feijao: escolhas.append("Feijão")
            if tem_mac: escolhas.append("Macarrão")
            
            detalhes_finais = f"{item['item']} ({carne}) + {', '.join(escolhas)}"
            st.session_state.carrinho.append({"item": detalhes_finais, "valor": p_final})
            st.toast(f"✅ Adicionado!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- SEÇÃO DE BEBIDAS ---
st.markdown('<div class="secao-titulo">🥤 BEBIDAS E SUCOS</div>', unsafe_allow_html=True)
bebidas = [x for x in dados.get('cardapio', []) if x.get('tipo') == "Bebida"]

for b, beb in enumerate(bebidas):
    p_orig = beb.get('preco', 0.0)
    em_promo = beb.get('em_promo', False)
    porcentagem = beb.get('porcentagem', 0)
    p_final = p_orig * (1 - (porcentagem / 100)) if em_promo else p_orig

    with st.container():
        st.markdown('<div class="item-container">', unsafe_allow_html=True)
        c_img, c_txt, c_btn = st.columns([0.8, 1.5, 0.7])
        with c_img:
            if beb.get('imagem'): st.image(beb['imagem'], use_container_width=True)
        with c_txt:
            st.write(f"**{beb['item']}**")
            if em_promo:
                st.error(f"PROMOÇÃO -{porcentagem}%")
                st.write(f"~~R$ {p_orig:.2f}~~")
                st.success(f"R$ {p_final:.2f}")
            else:
                st.write(f"R$ {p_orig:.2f}")
        with c_btn:
            if st.button("🛒", key=f"btn_b_b_{b}"):
                st.session_state.carrinho.append({"item": beb['item'], "valor": p_final})
                st.toast("✅ Adicionado!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- CARRINHO ---
if st.session_state.carrinho:
    st.markdown('<div class="secao-titulo">🛒 MEU CARRINHO</div>', unsafe_allow_html=True)
    total = 0
    for idx, item_car in enumerate(st.session_state.carrinho):
        cn, cv, cd = st.columns([2, 0.8, 0.7])
        cn.write(f"🔹 {item_car['item']}")
        cv.write(f"R$ {item_car['valor']:.2f}")
        if cd.button("Excluir", key=f"del_c_{idx}"):
            st.session_state.carrinho.pop(idx)
            st.rerun()
        total += item_car['valor']
    
    st.subheader(f"Total: R$ {total:.2f}")

    # CONSERTO 2: Fechando a chave corretamente (Resolve erro da imagem e26c38)
    if st.button("🚀 FINALIZAR PEDIDO", key="btn_final_cli"):
        dados_finais = carregar_dados()
        agora = datetime.now().strftime("%H:%M")
        for item_ped in st.session_state.carrinho:
            dados_finais['pedidos'].append({
                "id": int(time.time() * 1000), 
                "mesa": mesa_selecionada,
                "item": item_ped['item'], 
                "valor": item_ped['valor'],
                "status": "Pendente", 
                "hora": agora
            }) # <--- Chave fechada aqui!
        salvar_dados(dados_finais)
        st.session_state.carrinho = []
        st.success("✅ Pedido enviado!")
        time.sleep(2)
        st.rerun()