import chromadb
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

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
    
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 5, 'fetch_k': 50}
    )
    
    model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
    compressor = CrossEncoderReranker(model=model, top_n=3)
    compression_retriever = ContextualCompressionRetriever(
        compressor=compressor, base_retriever=retriever
    )
    
    return compression_retriever
