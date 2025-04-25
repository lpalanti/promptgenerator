import streamlit as st
import pandas as pd
import json
import os

# Configuração do layout
st.set_page_config(page_title="Prompt Generator", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #000000; color: #FFFFFF;}
    .prompt-box {border: 1px solid #f63366; padding: 10px; border-radius: 5px; background-color: #1c1c1c; position: fixed; top: 80px; right: 20px; width: 35%; max-height: 80vh; overflow-y: auto;}
    .category-title {color: #f63366; font-weight: bold; font-size: 20px; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# Função para carregar dados persistentes
def load_persistent_data(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return default_data

# Função para salvar dados persistentes
def save_persistent_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)

# Arquivo para armazenar itens manuais
ITEMS_FILE = "manual_items.json"

# Carregar o CSV
def load_data():
    return pd.read_csv("prompts_limpo.csv")

df = load_data()
manual_items = load_persistent_data(ITEMS_FILE, {})

# Dicionário de traduções (exemplos)
translations = {
    "forest": "floresta",
    "city": "cidade",
    "desert": "deserto",
    "mountain": "montanha",
    "river": "rio",
    "castle": "castelo",
    "sunset": "pôr do sol",
    "night": "noite",
    "dragon": "dragão",
    "unicorn": "unicôrnio"
}

# Inicializar estado da sessão
if "prompt_final" not in st.session_state:
    st.session_state.prompt_final = []

if "historico" not in st.session_state:
    st.session_state.historico = []

st.title("Prompt Generator")
st.markdown("Easily create and refine prompts for Stable Diffusion.")

# Sidebar de categorias
st.sidebar.title("Categories")
categorias = df["Categoria"].unique()
for categoria in categorias:
    with st.sidebar.expander(categoria):
        itens_base = df[df["Categoria"] == categoria]["Itens"].values[0].split(", ")
        itens_extras = manual_items.get(categoria, [])
        todos_itens = itens_base + itens_extras

        for item in todos_itens:
            tooltip = translations.get(item.lower(), "")
            if st.button(item, help=tooltip, key=f"{categoria}_{item}"):
                if item not in st.session_state.prompt_final:
                    st.session_state.prompt_final.append(item)

        # Campo para adicionar itens manualmente
        novo_item = st.text_input(f"Add new item to {categoria}", key=f"input_{categoria}")
        if st.button(f"Add to {categoria}", key=f"add_{categoria}"):
            if novo_item and novo_item not in todos_itens:
                manual_items.setdefault(categoria, []).append(novo_item)
                save_persistent_data(ITEMS_FILE, manual_items)
                st.experimental_rerun()

# Prompt final fixo
st.markdown('<div class="prompt-box">', unsafe_allow_html=True)

st.subheader("Prompt Final")

# Campo de edição manual
prompt_input = st.text_area("Edit manually:", ", ".join(st.session_state.prompt_final), height=200, label_visibility="collapsed")

# Atualizar prompt final ao editar manualmente
if prompt_input != ", ".join(st.session_state.prompt_final):
    st.session_state.prompt_final = [p.strip() for p in prompt_input.split(",") if p.strip()]

# Mostrar os itens clicáveis
st.markdown("### Click to remove items:")
for item in st.session_state.prompt_final:
    if st.button(f"\u274c {item}", key=f"remove_{item}"):
        st.session_state.prompt_final.remove(item)

# Salvar no histórico
if st.button("Save Prompt"):
    prompt_str = ", ".join(st.session_state.prompt_final)
    if prompt_str:
        st.session_state.historico.insert(0, prompt_str)
        st.session_state.historico = st.session_state.historico[:5]  # manter os últimos 5

# Mostrar histórico
st.markdown("### Last 5 Prompts:")
for past_prompt in st.session_state.historico:
    st.markdown(f"- {past_prompt}")

st.markdown('</div>', unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True)
