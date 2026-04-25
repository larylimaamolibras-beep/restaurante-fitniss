import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import time

# --- BANCO DE DADOS ---
DB_FILE = "banco_dados.json"
ARQUIVO_SENHAS = "usuarios_cadastrados.txt"

def carregar_dados():
    if not os.path.exists(DB_FILE):
        return {"cardapio": [], "pedidos": [], "vendas_finalizadas": []}
    with open(DB_FILE, "r", encoding='utf-8') as f: return json.load(f)

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding='utf-8') as f: json.dump(dados, f, indent=4)

def carregar_usuarios():
    usuarios = {"admin": "123"}
    if os.path.exists(ARQUIVO_SENHAS):
        with open(ARQUIVO_SENHAS, "r", encoding='utf-8') as f:
            for linha in f:
                if ":" in linha:
                    u, s = linha.strip().split(":")
                    usuarios[u] = s
    return usuarios

def salvar_usuario(u, s):
    with open(ARQUIVO_SENHAS, "a", encoding='utf-8') as f: f.write(f"{u}:{s}\n")

st.set_page_config(page_title="ADM PROFISSIONAL", layout="wide")

if 'logado' not in st.session_state: st.session_state.logado = False
dados = carregar_dados()
usuarios = carregar_usuarios()
META_DIARIA = 1500.00 

# --- CSS MANTEVE IGUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .banner-topo { 
        background-color: #00FF00; border-radius: 15px; padding: 15px; 
        color: black !important; font-size: 24px; font-weight: 900; 
        text-align: center; margin-bottom: 20px; 
    }
    h1, h2, h3, p, label { color: white !important; }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

if not st.session_state.logado:
    st.markdown('<div class="banner-topo">ACESSO RESTRITO - ADM</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 ENTRAR", "📝 CADASTRAR"])
        with tab1:
            with st.form("login"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("ACESSAR"):
                    if u in usuarios and usuarios[u] == p:
                        st.session_state.logado = True
                        st.rerun()
                    else: st.error("❌ Credenciais incorretas")
        with tab2:
            with st.form("cadastro"):
                nu = st.text_input("Novo Usuário")
                np = st.text_input("Nova Senha", type="password")
                if st.form_submit_button("SALVAR"):
                    if nu and np:
                        salvar_usuario(nu, np)
                        st.success("✅ Cadastrado!")
else:
    st.markdown('<div class="banner-topo">PAINEL DE GESTÃO DO CARDÁPIO</div>', unsafe_allow_html=True)
    
    # --- PARTE DAS MÉTRICAS E BOTÃO DE ZERAR ---
    total_vendas = sum(v['valor'] for v in dados.get('vendas_finalizadas', []))
    
    c1, c2, c3 = st.columns([1.5, 1.5, 1])
    c1.metric("VENDIDO HOJE", f"R$ {total_vendas:.2f}")
    c2.metric("META DIÁRIA", f"R$ {META_DIARIA:.2f}")
    
    # Botão para Zerar as Vendas (Começar novo dia)
    if c3.button("⚠️ FECHAR CAIXA (ZERAR)"):
        dados['vendas_finalizadas'] = []
        salvar_dados(dados)
        st.success("Caixa zerado para o novo dia!")
        time.sleep(1)
        st.rerun()

    abas = st.tabs(["📥 PEDIDOS", "⚙️ EDITAR CARDÁPIO"])

    with abas[0]:
        # Recarga automática para ver pedidos do celular
        dados = carregar_dados()
        pedidos_novos = [p for p in dados.get('pedidos', []) if p['status'] == "Pendente"]
        
        if not pedidos_novos:
            st.info("⌛ Aguardando novos pedidos... (Atualiza automático)")
            
        for p in pedidos_novos:
            st.warning(f"📍 Mesa: {p['mesa']} | 🛒 Item: {p['item']} | 💰 R$ {p['valor']:.2f}")
            if st.button(f"FINALIZAR #{p['id']}", key=f"f{p['id']}"):
                dados_atuais = carregar_dados()
                dados_atuais['vendas_finalizadas'].append({"valor": p['valor'], "hora": datetime.now().strftime("%H:%M")})
                for pr in dados_atuais['pedidos']:
                    if pr['id'] == p['id']: pr['status'] = "Concluido"
                salvar_dados(dados_atuais)
                st.rerun()

    with abas[1]:
        col_add1, col_add2 = st.columns(2)
        if col_add1.button("➕ NOVO PRATO"):
            dados['cardapio'].append({"item": "Novo Prato", "preco": 0.0, "imagem": "", "descricao": "", "tipo": "Prato"})
            salvar_dados(dados)
            st.rerun()
        if col_add2.button("➕ NOVA BEBIDA"):
            dados['cardapio'].append({"item": "Nova Bebida", "preco": 0.0, "imagem": "", "descricao": "", "tipo": "Bebida"})
            salvar_dados(dados)
            st.rerun()

        for i, item in enumerate(dados['cardapio']):
            tipo = item.get('tipo', 'Prato')
            cor_borda = "#00FF00" if tipo == "Prato" else "#00BFFF"
            with st.container():
                st.markdown(f'<div style="border-left: 10px solid {cor_borda}; background: #1a1c24; padding: 15px; border-radius: 5px; margin-bottom: 20px;">', unsafe_allow_html=True)
                c_img, c_info = st.columns([1, 3])
                with c_img:
                    url = st.text_input("URL Imagem", item['imagem'], key=f"img{i}")
                    if url: st.image(url, use_container_width=True)
                with c_info:
                    col_n, col_p, col_t = st.columns([2, 1, 1])
                    dados['cardapio'][i]['item'] = col_n.text_input("Nome", item['item'], key=f"n{i}")
                    dados['cardapio'][i]['preco'] = col_p.number_input("R$", float(item['preco']), key=f"p{i}")
                    dados['cardapio'][i]['tipo'] = col_t.selectbox("Tipo", ["Prato", "Bebida"], index=0 if tipo == "Prato" else 1, key=f"t{i}")
                    if st.button("✅ SALVAR", key=f"s{i}"):
                        dados['cardapio'][i]['imagem'] = url
                        salvar_dados(dados)
                        st.success("Salvo!")
                    if st.button("🗑️ EXCLUIR", key=f"del{i}"):
                        dados['cardapio'].pop(i)
                        salvar_dados(dados)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Refresh de 5 segundos para o ADM monitorar o celular
    time.sleep(5)
    st.rerun()