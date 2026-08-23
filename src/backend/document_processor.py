from pathlib import Path
from time import perf_counter
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
        use_multithreading=True,
        max_concurrency=4,
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
    total_start = perf_counter()

    docs_path = Path(docs_dir)

    print(f"\nLendo documentos de: {docs_path.absolute()}")

    load_start = perf_counter()

    documents = _load_documents(docs_path)

    print(f"Documentos carregados: {len(documents)}")
    print(f"[PERF] Carregamento dos documentos: {perf_counter() - load_start:.2f}s")

    if not documents:
        print("AVISO: nenhum documento foi carregado.")
        return []

    metadata_start = perf_counter()

    documents = _enrich_metadata(documents)

    print(f"[PERF] Metadados: {perf_counter() - metadata_start:.2f}s")

    split_start = perf_counter()

    chunks = _split_documents(documents)

    print(f"Chunks gerados: {len(chunks)}")
    print(f"[PERF] Chunking: {perf_counter() - split_start:.2f}s")

    print(
        f"[PERF] Processamento total dos documentos: "
        f"{perf_counter() - total_start:.2f}s"
    )

    return chunks
