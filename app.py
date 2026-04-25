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
    with open(DB_FILE, "r") as f: return json.load(f)

def salvar_dados(dados):
    with open(DB_FILE, "w") as f: json.dump(dados, f, indent=4)

def carregar_usuarios():
    usuarios = {"admin": "123"}
    if os.path.exists(ARQUIVO_SENHAS):
        with open(ARQUIVO_SENHAS, "r") as f:
            for linha in f:
                if ":" in linha:
                    u, s = linha.strip().split(":")
                    usuarios[u] = s
    return usuarios

def salvar_usuario(u, s):
    with open(ARQUIVO_SENHAS, "a") as f: f.write(f"{u}:{s}\n")

st.set_page_config(page_title="ADM PROFISSIONAL", layout="wide")

if 'logado' not in st.session_state: st.session_state.logado = False
dados = carregar_dados()
usuarios = carregar_usuarios()
META_DIARIA = 1500.00 

# --- CSS MELHORADO PARA LEITURA ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .banner-topo { 
        background-color: #00FF00; border-radius: 15px; padding: 15px; 
        color: black !important; font-size: 24px; font-weight: 900; 
        text-align: center; margin-bottom: 20px; 
    }
    .card-item {
        background-color: #1a1c24;
        border: 1px solid #00FF00;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    h1, h2, h3, p, label { color: white !important; }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN (MANTIDO) ---
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
    
    total_vendas = sum(v['valor'] for v in dados['vendas_finalizadas'])
    c1, c2 = st.columns(2)
    c1.metric("VENDIDO HOJE", f"R$ {total_vendas:.2f}")
    c2.metric("META DIÁRIA", f"R$ {META_DIARIA:.2f}")

    abas = st.tabs(["📥 PEDIDOS", "⚙️ EDITAR CARDÁPIO"])

    with abas[1]:
        # Botões de Adicionar
        col_add1, col_add2 = st.columns(2)
        if col_add1.button("➕ NOVO PRATO"):
            dados['cardapio'].append({"item": "Novo Prato", "preco": 0.0, "imagem": "", "descricao": "", "tipo": "Prato"})
            salvar_dados(dados)
            st.rerun()
        if col_add2.button("➕ NOVA BEBIDA"):
            dados['cardapio'].append({"item": "Nova Bebida", "preco": 0.0, "imagem": "", "descricao": "", "tipo": "Bebida"})
            salvar_dados(dados)
            st.rerun()

        st.write("---")

        # Listagem dos Itens para Editar
        for i, item in enumerate(dados['cardapio']):
            tipo = item.get('tipo', 'Prato')
            cor_borda = "#00FF00" if tipo == "Prato" else "#00BFFF"
            
            with st.container():
                st.markdown(f'<div style="border-left: 10px solid {cor_borda}; background: #1a1c24; padding: 15px; border-radius: 5px; margin-bottom: 20px;">', unsafe_allow_html=True)
                
                c_img, c_info = st.columns([1, 3])
                
                with c_img:
                    url = st.text_input("URL Imagem", item['imagem'], key=f"img{i}")
                    if url:
                        st.image(url, use_container_width=True)
                    else:
                        st.warning("Sem Foto")
                
                with c_info:
                    col_n, col_p, col_t = st.columns([2, 1, 1])
                    dados['cardapio'][i]['item'] = col_n.text_input("Nome do Item", item['item'], key=f"n{i}")
                    dados['cardapio'][i]['preco'] = col_p.number_input("Preço (R$)", float(item['preco']), key=f"p{i}")
                    dados['cardapio'][i]['tipo'] = col_t.selectbox("Tipo", ["Prato", "Bebida"], index=0 if tipo == "Prato" else 1, key=f"t{i}")
                    
                    if dados['cardapio'][i]['tipo'] == "Prato":
                        dados['cardapio'][i]['descricao'] = st.text_area("Descrição (Arroz, feijão...)", item.get('descricao', ''), key=f"d{i}")
                    
                    dados['cardapio'][i]['imagem'] = url
                    
                    # Ações do Item
                    btn_col1, btn_col2 = st.columns(2)
                    if btn_col1.button("✅ SALVAR ALTERAÇÃO", key=f"s{i}"):
                        salvar_dados(dados)
                        st.success("Atualizado com sucesso!")
                    
                    if btn_col2.button("🗑️ EXCLUIR ITEM", key=f"del{i}"):
                        dados['cardapio'].pop(i)
                        salvar_dados(dados)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

    with abas[0]:
        # Pedidos (Código mantido)
        pedidos_novos = [p for p in dados['pedidos'] if p['status'] == "Pendente"]
        for p in pedidos_novos:
            st.warning(f"Mesa: {p['mesa']} | Item: {p['item']} | R$ {p['valor']:.2f}")
            if st.button("FINALIZAR", key=f"f{p['id']}"):
                dados['vendas_finalizadas'].append({"valor": p['valor']})
                for pr in dados['pedidos']:
                    if pr['id'] == p['id']: pr['status'] = "Concluido"
                salvar_dados(dados)
                st.rerun()

    time.sleep(10)
    st.rerun()