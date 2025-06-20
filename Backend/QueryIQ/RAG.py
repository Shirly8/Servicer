import os
import shutil
import argparse
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_chroma import Chroma



CHROMA_PATH = "./VectorDB"
DATA_PATH = './Files'
db = None


# Function processes all PDFs
def load_documents():
    os.chdir('/Users/shirleyhuang/Documents/Apps/RAG')
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

#Split text into chunks of 800 texts
def split_documents(documents: list[Document]):
    chunk_size = 800
    chunk_overlap = int(chunk_size * 0.1) #10% overlap

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        length_function = len,
        is_separator_regex= False,
    )
    return text_splitter.split_documents(documents)

#Create page IDs (Files/Aretti.pdf: page number, chunk number)
def createIds(chunks):
    last_page_id = None
    index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        page_id = f"{source}:{page}"

        #Incremenet ID of the chunk if pageID on lastpage
        if page_id == last_page_id:
            index +=1
        else:
            index = 0
        
        #Assign the chunkID
        id = f"{page_id}:{index}"
        last_page_id = page_id

        #Add it as meta-data
        chunk.metadata["id"] = id

    return chunks


#Intialize Ollama vector embeddings from text data
def get_embedding():
    embeddings = OllamaEmbeddings(
        model = "nomic-embed-text"
    )
    return embeddings


#Initialize database:
def initialize_chroma():
    global db

    if db is None:
        db = Chroma(
            persist_directory = CHROMA_PATH, 
            embedding_function= get_embedding()
        )
    return db


#Manage vector database with ChromaDB storing embeddings (Source path, page number, chunk number)
def add_to_chroma(chunks: list[Document]):

    db = initialize_chroma()

    #Assign page IDs
    id_chunks = createIds(chunks)

    #Adding documents
    existing_items = db.get(include = [])
    existing_ids = set(existing_items["ids"]) if existing_items else set()
    print(f"Number of documents in the database: {len(existing_ids)}")

    #Creating chunks (That aren't in the DB)
    new_chunks = []
    for chunk in id_chunks:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if new_chunks:
        print(f"New Documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("No new documents to add")


def clear():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

def main():

    #Parse command-line
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    # Check if the database should be cleared (using the --reset flag)
    if args.reset:
        print("✨ Clearing Database")
        clear()

    # Load documents, split into chunks, and add them to Chroma
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


if __name__ == "__main__":
    main()


