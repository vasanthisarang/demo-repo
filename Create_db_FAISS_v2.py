
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
import os


# Step 1: Define paths
INDEX_DIR = "faiss_index_v2"
DATA_FILE = "c:/Vasanthi_New/Unofficial/Python_Sept2025/LangChain/Data/Books/awscdk.pdf"


# Step 2: Initialize embedding model
# embeddings_model = NomicEmbeddings(model="nomic-embed-text")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Step 3: Load or create FAISS index
if os.path.exists(INDEX_DIR):
    print("Loading existing FAISS index...")
    vectordb = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
else:
    print("Creating FAISS index from documents...")
    loader = PyPDFLoader(DATA_FILE)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    document = docs[21]
    print(document.page_content)
    print(document.metadata)
    selected_docs = [docs[21], docs[22]]
    # Convert chunks into embeddings and store in FAISS
    vectordb = FAISS.from_documents(selected_docs, embeddings)
    vectordb.save_local(INDEX_DIR)
    print("FAISS database creation completed.")

#embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#vectordb = FAISS.from_documents(docs, embedding_model)

#embeddings = OpenAIEmbeddings()
#db = FAISS.from_documents(docs, embeddings)
#db.save_local("FAISS_DB")


# Step 4: Load the LLM
llm = OllamaLLM(model="mistral")

# Step 5: Create RetrievalQA chain (RAG)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})
rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")

# Step 5: Ask a question
# query = "What are the Benefits of the AWS CDK?"
# query = "What are the two primary parts of AWS CDK?"
# query = "What are Supported programming languages for the AWS CDK?"
# query = "What are the languages spoken in India?"
query = "What is the chapter 4 title?"
result = rag_chain.invoke(query)
print("Answer:", result)
