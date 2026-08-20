import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCS_DIR = os.getenv("DOCS_DIR", os.path.join(BASE_DIR, "data", "docs"))

CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(BASE_DIR, "data", "chromadb"))

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env")
