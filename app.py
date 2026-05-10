import streamlit as st
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
    try:
        with open(DB_FILE, "r", encoding='utf-8') as f: 
            return json.load(f)
    except:
        return {"cardapio": [], "pedidos": [], "vendas_finalizadas": []}

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding='utf-8') as f: 
        json.dump(dados, f, indent=4, ensure_ascii=False)

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

# --- INICIALIZAÇÃO ---
if 'logado' not in st.session_state: st.session_state.logado = False

st.set_page_config(page_title="ADM PROFISSIONAL", layout="wide")

# LER DADOS NO TOPO PARA ATUALIZAÇÃO IMEDIATA
dados = carregar_dados()
usuarios = carregar_usuarios()
META_DIARIA = 1500.00 

# --- SEU CSS ORIGINAL (BANNER VERDE) ---
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
    .caixa-total-mesa {
        background-color: #1e1e24; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #00FF00; margin-bottom: 15px; margin-top: 10px;
    }
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
    
    # --- MÉTRICAS (VENDIDO HOJE) ---
    vendas_lista = dados.get('vendas_finalizadas', [])
    total_vendas = sum(float(v['valor']) for v in vendas_lista)
    
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 1])
    c1.metric("VENDIDO HOJE", f"R$ {total_vendas:.2f}")
    c2.metric("META DIÁRIA", f"R$ {META_DIARIA:.2f}")
    
    if c3.button("⚠️ FECHAR CAIXA"):
        dados['vendas_finalizadas'] = []
        salvar_dados(dados)
        st.rerun()

    if c4.button("🗑️ LIMPAR PEDIDOS"):
        dados['pedidos'] = []
        salvar_dados(dados)
        st.rerun()

    abas = st.tabs(["📥 PEDIDOS", "⚙️ EDITAR CARDÁPIO"])

    with abas[0]:
        pedidos_pendentes = [p for p in dados.get('pedidos', []) if p.get('status') == "Pendente"]
        
        if not pedidos_pendentes:
            st.info("⌛ Aguardando novos pedidos...")
        else:
            mesas_ativas = sorted(list(set([p['mesa'] for p in pedidos_pendentes])))
            for mesa in mesas_ativas:
                p_mesa = [p for p in pedidos_pendentes if p['mesa'] == mesa]
                t_mesa = sum([float(p['valor']) for p in p_mesa])
                
                st.markdown(f'<div class="caixa-total-mesa"><h3>📍 {mesa}</h3><h4>TOTAL: R$ {t_mesa:.2f}</h4></div>', unsafe_allow_html=True)
                
                for p in p_mesa:
                    col_info, col_btn = st.columns([3, 1])
                    col_info.write(f"🍴 {p['item']} | 💰 R$ {float(p['valor']):.2f}")
                    
                    # --- CONSERTO: A CHAVE PRECISA SER ÚNICA PARA RESPONDER ---
                    chave_finalizar = f"btn_fin_{p['id']}_{int(time.time() * 1000)}"
                    
                    if col_btn.button(f"FINALIZAR #{p['id']}", key=chave_finalizar):
                        db = carregar_dados()
                        
                        # 1. Registra a venda para somar no topo
                        venda = {"valor": float(p['valor']), "hora": datetime.now().strftime("%H:%M")}
                        db['vendas_finalizadas'].append(venda)
                        
                        # 2. Muda o status para sumir da lista de pendentes
                        for item in db['pedidos']:
                            if item['id'] == p['id']:
                                item['status'] = "Concluido"
                        
                        # 3. Salva e reinicia para o valor subir na hora
                        salvar_dados(db)
                        st.rerun()
                st.markdown("---")

    with abas[1]:
        col_add1, col_add2 = st.columns(2)
        if col_add1.button("➕ NOVO PRATO"):
            dados['cardapio'].append({"item": "Novo Prato", "preco": 0.0, "imagem": "", "tipo": "Prato", "em_promo": False, "porcentagem": 0})
            salvar_dados(dados)
            st.rerun()
        if col_add2.button("➕ NOVA BEBIDA"):
            dados['cardapio'].append({"item": "Nova Bebida", "preco": 0.0, "imagem": "", "tipo": "Bebida", "em_promo": False, "porcentagem": 0})
            salvar_dados(dados)
            st.rerun()

        for i, item in enumerate(dados['cardapio']):
            tipo = item.get('tipo', 'Prato')
            cor_borda = "#00FF00" if tipo == "Prato" else "#00BFFF"
            with st.container():
                st.markdown(f'<div style="border-left: 10px solid {cor_borda}; background: #1a1c24; padding: 15px; border-radius: 5px; margin-bottom: 20px;">', unsafe_allow_html=True)
                c_img, c_info = st.columns([1, 3])
                with c_img:
                    url_img = st.text_input("URL Imagem", item.get('imagem', ''), key=f"img{i}")
                    if url_img: st.image(url_img, use_container_width=True)
                with c_info:
                    col_n, col_p, col_t = st.columns([2, 1, 1])
                    dados['cardapio'][i]['item'] = col_n.text_input("Nome", item['item'], key=f"n{i}")
                    dados['cardapio'][i]['preco'] = col_p.number_input("R$ (Preço)", float(item['preco']), key=f"p{i}")
                    dados['cardapio'][i]['tipo'] = col_t.selectbox("Tipo", ["Prato", "Bebida"], index=0 if tipo == "Prato" else 1, key=f"t{i}")
                    
                    c_p1, c_p2 = st.columns(2)
                    em_promo = c_p1.checkbox("Ativar Promoção?", value=item.get('em_promo', False), key=f"promo_check{i}")
                    porcentagem = c_p2.number_input("% Desconto", value=int(item.get('porcentagem', 0)), key=f"promo_val{i}")
                    
                    if st.button("✅ SALVAR ALTERAÇÕES", key=f"s{i}"):
                        dados['cardapio'][i]['imagem'] = url_img
                        dados['cardapio'][i]['em_promo'] = em_promo
                        dados['cardapio'][i]['porcentagem'] = porcentagem
                        salvar_dados(dados)
                        st.success("Salvo!")
                    
                    if st.button("🗑️ EXCLUIR ITEM", key=f"del{i}"):
                        dados['cardapio'].pop(i)
                        salvar_dados(dados)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    time.sleep(10)
    st.rerun()