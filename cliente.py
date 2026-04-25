import streamlit as st
import json
import os
import time
from datetime import datetime

DB_FILE = "banco_dados.json"

def carregar_dados():
    if not os.path.exists(DB_FILE): return {"cardapio": [], "pedidos": []}
    with open(DB_FILE, "r") as f: return json.load(f)

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

st.set_page_config(page_title="Cardápio Restaurante Fitness", layout="centered")

# --- SEU ESTILO ORIGINAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
    .secao-titulo { 
        background-color: #00FF00; color: black !important; 
        padding: 10px; border-radius: 10px; text-align: center; 
        font-weight: 900; margin: 20px 0;
    }
    .item-container { 
        border: 2px solid #00FF00; padding: 15px; 
        border-radius: 15px; margin-bottom: 20px; background: #111; 
    }
    .badge-promo { 
        background: #ff4b4b; color: white; padding: 2px 8px; 
        border-radius: 5px; font-size: 14px; font-weight: bold;
    }
    .preco-antigo { color: #ff4b4b; text-decoration: line-through; font-size: 14px; }
    .preco-novo { color: #00FF00; font-size: 22px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

dados = carregar_dados()
mesa = st.sidebar.selectbox("📍 Sua Mesa", [f"Mesa {i:02d}" for i in range(1, 21)])

st.title("🍏 RESTAURANTE FITNESS")

# --- SEÇÃO DE PRATOS ---
st.markdown('<div class="secao-titulo">🍲 MONTE SEU PRATO</div>', unsafe_allow_html=True)
pratos = [item for item in dados['cardapio'] if item.get('tipo') == "Prato"]

for i, item in enumerate(pratos):
    with st.container():
        st.markdown('<div class="item-container">', unsafe_allow_html=True)
        col_img, col_info = st.columns([1, 1.5])
        with col_img:
            if item.get('imagem'): st.image(item['imagem'], use_container_width=True)
        with col_info:
            st.subheader(item['item'])
            st.write(f"R$ {item['preco']:.2f}")
            
        st.write("**O que vai no prato?**")
        c1, c2, c3 = st.columns(3)
        arroz = c1.checkbox("Arroz", value=True, key=f"ar_{i}")
        feijao = c2.checkbox("Feijão", value=True, key=f"fe_{i}")
        mac = c3.checkbox("Macarrão", value=True, key=f"ma_{i}")
        carne = st.radio("Proteína:", ["Frango", "Carne de Sol", "Fígado", "Bife", "Suíno", "Omelete"], key=f"prot_{i}")
        
        if st.button(f"🛒 PEDIR PRATO", key=f"btn_p_{i}"):
            dados_atuais = carregar_dados()
            escolhas = [opt for opt, val in zip(["Arroz", "Feijão", "Macarrão"], [arroz, feijao, mac]) if val]
            resumo = f"{item['item']} ({', '.join(escolhas)}) + {carne}"
            novo_p = {"id": int(time.time()), "mesa": mesa, "item": resumo, "valor": item['preco'], "pagamento": "No Caixa", "status": "Pendente", "hora": datetime.now().strftime("%H:%M")}
            dados_atuais['pedidos'].append(novo_p)
            salvar_dados(dados_atuais)
            st.success("✅ Adicionado!")
        st.markdown('</div>', unsafe_allow_html=True)

# --- SEÇÃO DE BEBIDAS COM PROMOÇÃO E FOTO ---
st.markdown('<div class="secao-titulo">🥤 BEBIDAS E SUCOS</div>', unsafe_allow_html=True)
bebidas_banco = [b for b in dados['cardapio'] if b.get('tipo') == "Bebida"]

for b, beb in enumerate(bebidas_banco):
    preco_original = beb['preco']
    preco_final = preco_original
    promo_label = ""
    
    # Lógica da Promoção
    if "detox" in beb['item'].lower():
        preco_final = preco_original * 0.80
        promo_label = "PROMO -20%"
    elif any(x in beb['item'].lower() for x in ["coca", "guaraná", "fanta", "refrigerante"]):
        preco_final = preco_original * 0.95
        promo_label = "PROMO -5%"

    with st.container():
        st.markdown('<div class="item-container">', unsafe_allow_html=True)
        col_b_img, col_b_txt, col_b_btn = st.columns([0.8, 1.5, 0.7])
        
        with col_b_img:
            if beb.get('imagem'): st.image(beb['imagem'], use_container_width=True)
            else: st.write("🥤")
            
        with col_b_txt:
            st.markdown(f"**{beb['item']}**")
            if promo_label:
                st.markdown(f'<span class="badge-promo">{promo_label}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="preco-antigo">R$ {preco_original:.2f}</span>', unsafe_allow_html=True)
                st.markdown(f'<span class="preco-novo">R$ {preco_final:.2f}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="preco-novo">R$ {preco_original:.2f}</span>', unsafe_allow_html=True)
        
        with col_b_btn:
            if st.button("🛒", key=f"btn_beb_{b}"):
                dados_atuais = carregar_dados()
                novo_b = {"id": int(time.time()), "mesa": mesa, "item": f"BEBIDA: {beb['item']}", "valor": preco_final, "pagamento": "No Caixa", "status": "Pendente", "hora": datetime.now().strftime("%H:%M")}
                dados_atuais['pedidos'].append(novo_b)
                salvar_dados(dados_atuais)
                st.toast(f"✅ {beb['item']} no carrinho!")
        st.markdown('</div>', unsafe_allow_html=True)

# Sincronização automática para aparecer no ADM
time.sleep(10)
st.rerun()