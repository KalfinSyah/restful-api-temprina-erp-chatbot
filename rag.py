from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def get_hugging_face_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base"
    )

def vectorstrore_FAISS(documets, embedding_model = get_hugging_face_embedding_model()):
    return FAISS.from_documents(documets, embedding_model)

def retrival(query, vectorstore, k):
    return vectorstore.similarity_search(query, k=k)