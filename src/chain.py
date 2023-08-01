from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from src.SwitchLLM import switchLLM as llm
from langchain.text_splitter import RecursiveCharacterTextSplitter
import nomic
from nomic import atlas
import numpy as numpy
import os.path
from langchain.chains import RetrievalQA
from langchain import PromptTemplate


def get_text_chunks(text):
        text_splitter = RecursiveCharacterTextSplitter(
        separators=[" ", ",", "\n"],
        chunk_size=800, #the size of the chunk itself. 1000 characters 
        chunk_overlap=200, #you may lose some context if you end in the middle. starts the next chunk a few characters before. 
        length_function=len
    )
        chunks = text_splitter.split_text(text)
        return chunks
    
    
def get_vectorstore(text_chunks):
    #embeddings =HuggingFaceInstructEmbeddings(model_name="intfloat/e5-large-v2")
    embeddings = HuggingFaceInstructEmbeddings(model_name="thenlper/gte-large")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    return vectorstore

def get_embeddings(text_chunks):
    #embeddings =HuggingFaceInstructEmbeddings(model_name="intfloat/e5-large-v2")
    embeddings =HuggingFaceInstructEmbeddings(model_name="thenlper/gte-large")
    return embeddings.embed_documents(text_chunks)
    

def get_conversation_chain(vectorstore,llm):
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

    
def qa(vectorstore,llm, query):
    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    {context}
    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"])
    chain_type_kwargs = {"prompt": PROMPT}

    qa =RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(),chain_type_kwargs=chain_type_kwargs)
    result=qa.run(query)
    return result
                          
                       
