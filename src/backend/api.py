from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.backend.rag_agent import CorporateAgent
from src.backend.vector_store import VectorStoreManager

app = FastAPI(title="Corporate RAG Agent API")

vector_manager = VectorStoreManager()
agent = CorporateAgent(vector_manager)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "chunks": vector_manager.vector_store._collection.count(),
    }


@app.post("/chat")
def chat_endpoint(request: QueryRequest):

    try:
        answer = agent.ask(request.question)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync")
def sync_documents_endpoint():

    try:
        result = vector_manager.sync_documents()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/search")
def debug_search(request: QueryRequest):

    try:
        docs = vector_manager.search(request.question, k=5)

        return {
            "results": [
                {
                    "filename": doc.metadata.get("filename", "Desconhecido"),
                    "content": doc.page_content,
                }
                for doc in docs
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
