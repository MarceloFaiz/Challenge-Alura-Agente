from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300


def _get_file_metadata(filepath):
    """Extrai metadados essenciais do arquivo."""
    path = Path(filepath)
    stat = path.stat()

    return {
        "source": str(path),
        "filename": path.name,
        "last_modified": stat.st_mtime,
    }


def _load_documents(docs_dir):
    """Carrega todos os documentos do diretório."""
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.*",
        loader_cls=UnstructuredFileLoader,
        show_progress=True,
    )

    return loader.load()


def _enrich_metadata(documents):
    """Adiciona metadados dos arquivos aos documentos carregados."""

    for document in documents:
        filepath = document.metadata.get("source")

        if filepath and Path(filepath).exists():
            document.metadata.update(_get_file_metadata(filepath))

        print(
            f"Arquivo: "
            f"{document.metadata.get('filename', 'Desconhecido')} | "
            f"Caracteres: {len(document.page_content)}"
        )

    return documents


def _split_documents(documents):
    """Divide os documentos em chunks."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return text_splitter.split_documents(documents)


def load_and_process_documents(docs_dir):
    """
    Carrega documentos do diretório, adiciona metadados
    e divide o conteúdo em chunks.
    """

    docs_path = Path(docs_dir)

    print(f"\nLendo documentos de: {docs_path.absolute()}")

    documents = _load_documents(docs_path)

    print(f"Documentos carregados: {len(documents)}")

    if not documents:
        print("AVISO: nenhum documento foi carregado.")
        return []

    documents = _enrich_metadata(documents)

    chunks = _split_documents(documents)

    print(f"Chunks gerados: {len(chunks)}")

    return chunks
