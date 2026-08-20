from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.rag_agent import CorporateAgent
from src.vector_store import VectorStoreManager

app = FastAPI(title="Corporate RAG Agent API")

vector_manager = VectorStoreManager()
agent = CorporateAgent(vector_manager)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "chunks": vector_manager.vector_store._collection.count(),
    }


@app.post("/chat")
async def chat_endpoint(request: QueryRequest):

    try:
        answer = agent.ask(request.question)

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync")
async def sync_documents_endpoint():

    try:
        result = vector_manager.sync_documents()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/search")
async def debug_search(request: QueryRequest):
    
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
