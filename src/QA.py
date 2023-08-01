import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.chains import RetrievalQA

class QA:
    def __init__(self) -> None:
        pass
    
    def get_text_chunks(self,text,chunk_size=800,chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
        separators=[" ", ",", "\n"],
        chunk_size=800, 
        chunk_overlap=200,
        length_function=len
    )
        chunks = text_splitter.split_text(text)
        return chunks
    
    
    def get_vectorstore(self,text_chunks,model_name):
        embeddings = HuggingFaceInstructEmbeddings(model_name=model_name)
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

        return vectorstore
    
    def get_embeddings(self,text_chunks,model_name):
        embeddings =HuggingFaceInstructEmbeddings(model_name=model_name)
        return embeddings.embed_documents(text_chunks)
    
    def get_conversation_chain(self,vectorstore,llm):
        memory = ConversationBufferMemory(
            memory_key='chat_history', return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        return conversation_chain

    def getRetrievalQA(self,vectorstore,llm,):
        return RetrievalQA.from_chain_type(llm,retriever=vectorstore.as_retriever())
        
    

    