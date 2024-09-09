from dotenv import load_dotenv
import tempfile
import shutil
import time
import os

from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.embeddings import OllamaEmbeddings
import streamlit as st

# Load environment variables
load_dotenv()
st.set_page_config(page_title="ATS Resume EXpert ")
st.write("Converts pdf to embeddings and uses Llama3 from ollama (Local llm) as LLM")
st.title("ATS TRACKING SYSTEM")

# Upload PDF
uploaded_file = st.file_uploader(label="Upload Your PDF")

submit = st.button("Tell me about the resume")
prompt = "Tell me about the resume"
if submit:
    if uploaded_file is not None:
        # Save as tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            shutil.copyfileobj(uploaded_file, tmpfile)
            file_path = tmpfile.name

        try:
            # Load PDF using PyPDFLoader
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            st.write("Data Loading Started")

            # Split documents into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
            chunks = splitter.split_documents(docs)

            # Initialize LLM and embeddings
            llm = Ollama(model="llama3")
            embeddings = OllamaEmbeddings(model="llama3")
            vector_store = FAISS.from_documents(documents=chunks[:25], embedding=embeddings)
            st.write("Embedding Vector Started")
            time.sleep(2)  # Simulate processing time

            # Create retriever
            retriever = vector_store.as_retriever()

            # Setup the RetrievalQA chain (no sources)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever
            )

            # Perform the query
            query = "Tell me about the resume"
            response = qa_chain.run(query)

            st.header("Answer")
            st.write(response)

        except Exception as e:
            st.error(f"An error occurred: {e}")

        finally:
            # Clean up temporary file
            os.remove(file_path)
    else:
        st.write("Please upload a PDF file.")
