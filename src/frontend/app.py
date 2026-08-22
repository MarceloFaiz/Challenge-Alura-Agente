import streamlit as st
import requests
import os

# URL da API FastAPI (rodando localmente)
# API_URL = "http://localhost:8000"
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Agente Corporativo IA", page_icon="🧠", layout="centered"
)

st.title("🧠 Assistente de Conhecimento Corporativo")
st.markdown(
    "Faça perguntas sobre os documentos da empresa (RH, Projetos, Manuais, etc)."
)

# Botão lateral para forçar atualização da base de dados
with st.sidebar:
    st.header("Gerenciamento de Documentos")
    if st.button("🔄 Sincronizar Documentos"):
        with st.spinner("Analisando pastas e atualizando base vetorial..."):
            try:
                res = requests.post(f"{API_URL}/sync")
                if res.status_code == 200:
                    st.success("Base atualizada com sucesso!")
                else:
                    st.error("Erro ao sincronizar.")
            except Exception as e:
                st.error(
                    "A API FastAPI não está rodando. Inicie com: uvicorn src.api:app"
                )

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura nova pergunta
if prompt := st.chat_input("Pergunte algo sobre a empresa..."):
    # Adiciona a mensagem do usuário na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Consulta a API FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Buscando nos documentos..."):
            try:
                response = requests.post(f"{API_URL}/chat", json={"question": prompt})
                if response.status_code == 200:
                    answer = response.json().get(
                        "answer", "Erro ao processar resposta."
                    )
                else:
                    answer = f"Erro na API: {response.text}"
            except Exception:
                answer = "Erro de conexão. Certifique-se de que a FastAPI está rodando (`uvicorn src.api:app --reload`)."

            st.markdown(answer)

    # Salva resposta no histórico
    st.session_state.messages.append({"role": "assistant", "content": answer})
