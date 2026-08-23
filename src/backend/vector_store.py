import os

from time import perf_counter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from src.backend.config import CHROMA_DIR, DOCS_DIR
from src.backend.document_processor import load_and_process_documents

COLLECTION_NAME = "company_docs"


class VectorStoreManager:
    def __init__(self):
        print(f"Diretório dos documentos: {os.path.abspath(DOCS_DIR)}")

        print(f"Diretório do Chroma: {os.path.abspath(CHROMA_DIR)}")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.vector_store = self._create_vector_store()

        print(f"Chunks atualmente no Chroma: {self._get_count()}")

    def _create_vector_store(self):
        """Cria ou abre a coleção persistente do Chroma."""

        return Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=self.embeddings,
            collection_name=COLLECTION_NAME,
        )

    def _get_count(self):
        """Retorna a quantidade atual de chunks armazenados."""

        return self.vector_store._collection.count()

    def _delete_collection(self):
        """Remove a coleção atual do Chroma."""

        try:
            self.vector_store.delete_collection()

        except Exception as exc:
            print(f"Aviso ao remover coleção existente: {exc}")

    def sync_documents(self):
        """
        Reconstrói a base vetorial a partir dos documentos atuais.
        """

        print("\n=== SINCRONIZAÇÃO ===")

        print(f"Diretório: {os.path.abspath(DOCS_DIR)}")

        if not os.path.exists(DOCS_DIR):
            return {
                "status": "error",
                "message": (f"Diretório não encontrado: {DOCS_DIR}"),
            }

        chunks = load_and_process_documents(DOCS_DIR)

        if not chunks:
            return {
                "status": "error",
                "message": ("Nenhum chunk foi gerado a partir dos documentos."),
            }

        print(f"Chunks a adicionar: {len(chunks)}")

        # Remove a coleção atual
        self._delete_collection()

        # Cria uma nova coleção
        self.vector_store = self._create_vector_store()

        print("Gerando embeddings e armazenando chunks no Chroma...")

        embedding_start = perf_counter()

        self.vector_store.add_documents(chunks)

        embedding_time = perf_counter() - embedding_start

        print(f"[PERF] Embeddings + gravação no Chroma: {embedding_time:.2f}s")

        count = self._get_count()

        print(f"Chunks no Chroma após sincronização: {count}")

        return {
            "status": "success",
            "message": ("Banco de dados atualizado com sucesso."),
            "chunks": count,
        }

    def search(self, question, k=5):
        """Busca documentos semelhantes à pergunta."""

        search_start = perf_counter()

        docs = self.vector_store.similarity_search(
            question,
            k=k,
        )

        search_time = perf_counter() - search_start

        print(f"\nBusca: {question}")
        print(f"Resultados encontrados: {len(docs)}")
        print(f"[PERF] Embedding da pergunta + busca no Chroma: {search_time:.2f}s")

        # for i, doc in enumerate(docs):
        # print(f"\n--- Resultado {i + 1} ---")
        # print(f"Arquivo: {doc.metadata.get('filename', 'Desconhecido')}")
        # print(f"Conteúdo: {doc.page_content[:500]}")

        print(
            "Arquivos recuperados: "
            + ", ".join(doc.metadata.get("filename", "Desconhecido") for doc in docs)
        )

        return docs
