from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os
import app

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    temperature=0.4, 
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

def load_documents(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(directory, filename), encoding="utf-8")
            documents.extend(loader.load())
    return documents

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

def create_vector_store(documents):
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

def build_langchain_pipeline(directory):
    print("Loading documents...")
    documents = load_documents(directory)
    print(f"Loaded {len(documents)} documents.")
    
    print("Splitting documents into chunks...")
    document_chunks = split_documents(documents)
    print(f"Created {len(document_chunks)} document chunks.")
    
    print("Creating vector store...")
    vector_store = create_vector_store(document_chunks)
    
    retriever = vector_store.as_retriever()
    
    prompt_template = """Use the following context to answer the question. 
    If the answer is not in the context, say "I don't have enough information to answer this question."

    Context: {context}

    Question: {input}
    """
    prompt = PromptTemplate.from_template(prompt_template)

    document_chain = create_stuff_documents_chain(
        llm, 
        prompt
    )

    # Create retrieval chain
    retrieval_chain = create_retrieval_chain(
        retriever, 
        document_chain
    )
    
    return retrieval_chain

def interactive_qa_session(retrieval_chain):
    print("\nWelcome to the LangChain QA System!")
    print("Type 'quit' to exit the session")
    
    while True:
        print("\nEnter your question:")
        question = input("> ").strip()
        
        if question.lower() == 'quit':
            break
        
        response = retrieval_chain.invoke({"input": question})
        print("\nAnswer:")
        print(response['answer'])

if __name__ == "__main__":
    input_directory = app.OUTPUT_DIR  
    qa_chain = build_langchain_pipeline(input_directory)
    interactive_qa_session(qa_chain)
    
