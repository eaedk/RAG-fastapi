import os
import chromadb
from dotenv import load_dotenv
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma
import uvicorn

# ----------------------
# Configuration and Setup
# ----------------------

# Load environment variables from .env file
load_dotenv()

# Directories for file upload and persistent storage of Chroma vector database
UPLOAD_DIR = "uploads"
CHROMA_DIR = "chroma_db"

# Set model versions for LLM and embeddings
LLM = "gpt-4o-mini-2024-07-18"
EMBEDDING_MODEL = "text-embedding-3-small"

# Ensure necessary directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# Set OpenAI API key from environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize a persistent client for Chroma, specifying where the data is stored
client = chromadb.PersistentClient(path=CHROMA_DIR)

# FastAPI application setup
app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing) for all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# LangChain Initialization
# ----------------------

# Initialize the embedding model using OpenAI's API
embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)

# Initialize the language model (LLM) using OpenAI's API (with temperature for creativity)
llm = init_chat_model(model=LLM, model_provider="openai", temperature=0)

# Text splitter to split documents into manageable chunks (for efficient processing)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)

# Set up Chroma vector store to store document embeddings and their metadata
vectorstore = Chroma(
    client=client,
    persist_directory=CHROMA_DIR,
    embedding_function=embedding,
    collection_name="legal_docs"
)

# Define the prompt template that will be used in the LLM for querying with context
prompt_template = """
Tu es un assistant utile qui réponds en français de manière claire et concise.
Réponds uniquement en utilisant le contexte fourni.
Si tu ne sais pas, dis "Je ne sais pas".

contexte : {context}

question : {question}

answer :
"""

# Initialize the prompt template with variables
prompt = PromptTemplate(
    input_variables=["question", "context"],
    template=prompt_template,
)

# Function to format documents for easier reading (used for retriever output)
def format_docs(docs):
    return "\n\n".join([f"(Page {d.metadata.get('page','?')}) {d.page_content}" for d in docs])

# Set up the retriever to pull relevant documents from the vector store based on a query
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Define the QA chain that links together the retriever, document formatting, and LLM for querying
qa_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ----------------------
# Document Management Functions
# ----------------------

# Function to add a PDF document to the vector store (embedding and splitting into chunks)
def add_pdf_to_vectorstore(file_path):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Split the document into smaller chunks
    docs = text_splitter.split_documents(documents)

    # Generate a unique ID for each chunk
    uuids = [str(uuid4()) for _ in range(len(docs))]
    print(f"Number of documents split: {len(docs)}")

    # Add documents to the vector store (Chroma)
    vectorstore.add_documents(documents=docs, ids=uuids)

# ----------------------
# FastAPI Routes
# ----------------------

# Route to upload a PDF file and add its content to the vector store
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Check if the uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    # Save the uploaded file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
       buffer.write(await file.read())

    # Add the PDF document to the vector store
    add_pdf_to_vectorstore(file_path)

    # Return a success message
    content = {"message": f"Fichier {file.filename} ajouté à la base de connaissances."}
    print(f"{content=}")
    return JSONResponse(content=content)

# Route to interact with the assistant via a chat-like interface
@app.get("/chat/")
async def chat(message: str):
    # Use the QA chain to get a response from the assistant
    response = qa_chain.invoke(message)
    
    # Return the response from the assistant
    print(f"{response=}")
    return {"answer": response}

# ----------------------
# Streaming Response for Chat
# ----------------------

# This function will simulate the streaming of the response.
async def stream_chat_response(message: str):
    # Initialize the chat model (this could be done outside the function if it's expensive)
    # response_parts = []
    # print("Streaming API response:\n")
    async for part in qa_chain.astream(message):
        # response_parts.append(part)  # Collect all parts of the response
        # Yield each part as a chunk for streaming to the client
        print(part, end="", flush=True)
        yield part

    # # Final join to return the complete response after streaming
    # full_response = "".join(response_parts)
    # yield full_response

# FastAPI endpoint for streaming chat responses
@app.get("/chat_stream/")
async def chat_stream(message: str):
    """
    Endpoint to stream chat responses progressively.
    """
    # Return a StreamingResponse that will stream the response from the generator
    return StreamingResponse(stream_chat_response(message), media_type="text/plain")

# ----------------------
# Start the FastAPI app using Uvicorn
# ----------------------
if __name__ == "__main__":
    # Run the FastAPI application with auto-reloading enabled
    uvicorn.run(app, host="0.0.0.0", port=8000)
