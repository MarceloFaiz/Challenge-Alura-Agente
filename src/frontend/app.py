import streamlit as st
import requests
import uuid
import os


# URL da API FastAPI (rodando localmente)
API_URL = os.getenv("API_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Agente Corporativo IA", page_icon="🧠", layout="centered"
)


st.title("🧠 Assistente de Conhecimento Corporativo")
st.markdown(
    "Faça perguntas sobre os documentos da empresa (RH, Projetos, Manuais, etc)."
)


# Inicializa o histórico das conversas
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation" not in st.session_state:
    conversation_id = str(uuid.uuid4())

    st.session_state.conversations[conversation_id] = {
        "title": "Nova conversa",
        "messages": [],
    }

    st.session_state.current_conversation = conversation_id


# Sidebar
with st.sidebar:
    st.header("Conversas")

    if st.button("➕ Nova conversa", use_container_width=True):
        conversation_id = str(uuid.uuid4())

        st.session_state.conversations[conversation_id] = {
            "title": "Nova conversa",
            "messages": [],
        }

        st.session_state.current_conversation = conversation_id
        st.rerun()

    st.divider()

    # Exibe as conversas existentes
    for conversation_id, conversation in st.session_state.conversations.items():
        if st.button(
            conversation["title"],
            key=f"conversation_{conversation_id}",
            use_container_width=True,
        ):
            st.session_state.current_conversation = conversation_id
            st.rerun()

    st.divider()

    # Gerenciamento de documentos
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


# Obtém a conversa atualmente selecionada
current_conversation = st.session_state.conversations[
    st.session_state.current_conversation
]


# Exibe mensagens anteriores
for message in current_conversation["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Captura nova pergunta
if prompt := st.chat_input("Pergunte algo sobre a empresa..."):
    # Usa a primeira pergunta como título da conversa
    if not current_conversation["messages"]:
        title = prompt.strip()

        if len(title) > 40:
            title = title[:40].rstrip() + "..."

        current_conversation["title"] = title

    # Adiciona a mensagem do usuário na conversa atual
    current_conversation["messages"].append({"role": "user", "content": prompt})

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
                answer = (
                    "Erro de conexão. Certifique-se de que a FastAPI "
                    "está rodando (`uvicorn src.api:app --reload`)."
                )

            st.markdown(answer)

    # Salva resposta no histórico da conversa atual
    current_conversation["messages"].append({"role": "assistant", "content": answer})
