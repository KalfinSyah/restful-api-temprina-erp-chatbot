from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

def get_hugging_face_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def vectorstrore_FAISS(documets, embedding_model = get_hugging_face_embedding_model()):
    return FAISS.from_documents(documets, embedding_model)

def retrival(query, vectorstore, k):
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    compressor = CrossEncoderReranker(
        model=HuggingFaceCrossEncoder(
            model_name="BAAI/bge-reranker-v2-m3",
            model_kwargs={"device": "cpu"},
        ), 
        top_n=k
    )
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=base_retriever
    )
    return compression_retriever.invoke(query)