import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

CACHE = 'chromadb_persist'

def split_texts(text):
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    texts = text_splitter.split_text(text)
    return texts
    
    
def get_retriever(id, text):
    texts = split_texts(text)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # try:
    #     client = chromadb.PersistentClient(path=CACHE)
    #     db = Chroma(
    #         client=client,
    #         collection_name=id,
    #         embedding_function=embeddings,
    #     )

    # except Exception as e:
    #     print(e)
        
    db = Chroma.from_texts(
        texts,
        embedding=embeddings,
        collection_name=id,
        persist_directory=CACHE,
    )
    
    return db.as_retriever(
            search_type='mmr'
        ) 
    
    