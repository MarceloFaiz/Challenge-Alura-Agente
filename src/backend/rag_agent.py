from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# from langchain_community.document_compressors import FlashrankRerank

from src.config import GOOGLE_API_KEY


class CorporateAgent:

    FALLBACK_MESSAGE = (
        "Desculpe, não encontrei informações sobre isso "
        "nos documentos atuais da empresa."
    )

    def __init__(self, vector_manager):
        self.vector_manager = vector_manager

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.0,
        )

        # Reranker configurado para retornar os 3 melhores documentos
        # self.compressor = FlashrankRerank(top_n=3)

        self.prompt = self._build_prompt()

        self.chain = self.prompt | self.llm

    def _build_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
        Você é um assistente de IA corporativo.

        Sua função é responder perguntas sobre a empresa
        utilizando exclusivamente as informações presentes
        na base de documentos fornecida.

        REGRAS:

        1. Use somente informações presentes no contexto.
        2. Não utilize conhecimento externo para completar a resposta.
        3. Não invente informações.
        4. Se o contexto possuir informações suficientes para responder,
        responda normalmente.
        5. Se o contexto realmente não possuir informações relevantes,
        responda exatamente:

        "Desculpe, não encontrei informações sobre isso nos documentos atuais da empresa."

        6. Seja claro, objetivo e profissional.

        CONTEXTO:

        {context}
        """,
                ),
                (
                    "human",
                    "{question}",
                ),
            ]
        )

    def _retrieve_documents(self, question):
        return self.vector_manager.search(
            question,
            k=5,
        )

    def _build_context(self, documents):
        context_parts = []

        for document in documents:
            filename = document.metadata.get(
                "filename",
                "Desconhecido",
            )

            context_parts.append(f"[FONTE: {filename}]\n" f"{document.page_content}")

        return "\n\n".join(context_parts)

    def _extract_sources(self, documents):
        return list(
            set(
                document.metadata.get("filename", "Desconhecido")
                for document in documents
            )
        )

    def _generate_response(self, context, question):
        response = self.chain.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        if isinstance(response.content, str):
            return response.content

        if isinstance(response.content, list):
            return "\n".join(
                block["text"]
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )

        return str(response.content)

    def _append_sources(self, answer, sources):
        if not sources:
            return answer

        sources_text = "\n\n---\n\n**Fontes consultadas:**\n"
        sources_text += "\n".join(f"- `{source}`" for source in sources)

        return answer + sources_text

    def ask(self, question: str):

        documents = self._retrieve_documents(question)

        if not documents:
            return self.FALLBACK_MESSAGE

        context = self._build_context(documents)
        sources = self._extract_sources(documents)

        answer = self._generate_response(
            context,
            question,
        )

        return self._append_sources(
            answer,
            sources,
        )
