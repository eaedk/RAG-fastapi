# RAG-FastAPI

This project provides a simple **Retrieval-Augmented Generation (RAG)** system using **FastAPI**, **LangChain**, and **Chroma** for managing document-based queries. It allows users to upload PDFs, store their content in a vector database, and interact with a chatbot interface powered by GPT-models. Additionally, it supports streaming responses from the system.

## Project Structure

```
RAG-fastapi
├── _app.py                     # Main FastAPI app file
├── assets                      # Folder containing images for documentation and UI
│   ├── imgs                   
├── chroma_db                   # Persistent storage for Chroma vector database
│   └── chroma.sqlite3          # Chroma database file
├── fastapi                     # FastAPI related components and utilities
├── requirements.txt            # List of project dependencies
├── test.py                     # Testing script for functionality
└── uploads                     # Folder for storing uploaded PDF files
    └── example.pdf             # Sample PDF file uploaded for processing
```

## Requirements

This project uses the following libraries and tools:

* **FastAPI** for building the web application.
* **Chroma** for vector storage and document retrieval.
* **LangChain** for managing language models and document processing.
* **OpenAI** for leveraging GPT-4 and embedding models.
* **Uvicorn** as the ASGI server for running FastAPI.
* **dotenv** for managing environment variables.

### Install dependencies

You can install all the dependencies using `pip` by running:

```bash
pip install -r requirements.txt
```

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/eaedk/RAG-fastapi.git
   cd RAG-fastapi
   ```

2. **Environment Configuration**:

   Ensure that you have an `.env` file with the necessary environment variables. Specifically, you need your `OPENAI_API_KEY`.

   Example `.env`:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Create necessary directories**:

   If not already created, you need to manually create the following directories:

   * `uploads/`: For storing the uploaded PDF files.
   * `chroma_db/`: For storing the Chroma vector database.

4. **Run the application**:

   You can start the FastAPI app using Uvicorn:

   ```bash
   uvicorn _app:app --host 0.0.0.0 --port 8000 --reload
   ```

   This will start the server on `http://localhost:8000`.

## Endpoints

### 1. **Upload PDF** (`POST /upload/`)

This endpoint allows users to upload PDF files. The contents of the PDF will be processed and stored in the Chroma vector database.

* **Request**:

  * Form-data with a file (PDF).
* **Response**:

  * JSON message confirming the file upload.

### 2. **Chat Interface** (`GET /chat/`)

This endpoint allows users to interact with the chatbot. You can send a question, and the model will use the documents stored in the Chroma vector database to generate a response.

* **Request**:

  * A `message` query parameter.

* **Response**:

  * JSON with the assistant's answer.

### 3. **Chat Streaming** (`GET /chat_stream/`)

This endpoint provides a streaming response for the chat. As the response is generated, parts of it are streamed to the client.

* **Request**:

  * A `message` query parameter.

* **Response**:

  * Streaming plain text (with the assistant's answer).

## Testing

You can test the functionality of the endpoints using the provided docs page `localhost:8000/docs` or using tools like `Postman` or `curl` to interact with the API.

Example of testing the chat endpoint with `curl`:

```bash
curl -X 'GET' 'http://localhost:8000/chat_stream/?message=What+is+LLM' --header 'accept: text/plain' 
```

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/chat_stream/?message=de%20quoi%20parle%20le%20fichier%20%3F%20structure%20ta%20reponse' \
  -H 'accept: application/json' --no-buffer
```

## File Structure

* **Uploads Directory (`uploads/`)**: Contains the PDF files that are uploaded via the `/upload/` endpoint.
* **Chroma Database (`chroma_db/`)**: Stores the indexed documents in a vectorized format.
* **Assets Directory (`assets/`)**: Contains images used for the web interface or documentation.

## Example Walkthrough

1. **Upload a PDF**:

   * Upload a PDF using the `/upload/` endpoint. For example, you can upload a PDF like the `Transformers and LLMs Cheatsheet →.pdf` file.

2. **Query the Chat**:

   * Use the `/chat/` endpoint to ask a question based on the document you just uploaded.

3. **Stream the Response**:

   * You can also try the `/chat_stream/` endpoint to receive a streaming response from the assistant.

## Screenshots

Here are some screenshots of the FastAPI UI for reference:

* ![FastAPI Chat Interface](assets/imgs/fastapi-chat-2025-08-21_at_13.29.10.jpeg)
* ![FastAPI Docs](assets/imgs/fastapi-docs-2025-08-21_at_13.33.54.png)
* ![FastAPI Upload Interface](assets/imgs/fastapi-upload-2025-08-21_at_13.30.30.jpeg)

## Contributing

If you would like to contribute to this project, feel free to fork the repository and create a pull request. For any issues or enhancements, please open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
