# Twilight AI

Twilight AI is a chatbot based on the *Twilight* saga. I developed this project to create an assistant that can answer questions about the characters, vampire covens, relationships, and events from the story.

The application uses **Retrieval-Augmented Generation (RAG)**, which means the chatbot searches for information in documents before generating an answer. This helps it respond based on the information available in the project instead of only using what the language model already knows.

I used **React** for the frontend, **FastAPI** for the backend, **LangGraph** to organize the chatbot's workflow, **Ollama** to run the language model locally, and **ChromaDB** to store and search document information.

## Features

The application includes:

- A chatbot that answers questions about the Twilight saga.
- A RAG system that searches documents before answering.
- Conversation history so users can continue previous chats.
- User registration and login.
- JWT authentication.
- Two user roles: regular user and administrator.
- A document section where administrators can upload, view, and delete TXT files.
- Duplicate document validation.
- A React interface inspired by the Twilight aesthetic.

If the chatbot cannot find enough information to answer a question, it is instructed to say so instead of inventing an answer.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | API development |
| React | User interface |
| Vite | Frontend development |
| LangChain | Working with documents and language models |
| LangGraph | Organizing the chatbot workflow |
| Ollama | Running the language model locally |
| Qwen 2.5 (3B) | Language model |
| ChromaDB | Storing and searching document embeddings |
| Hugging Face Embeddings | Converting text into vectors |
| SQLite | Storing users and conversations |
| JWT | User authentication |
| pytest | Backend testing |

## How the Chatbot Works

When a user sends a question, the application follows these steps:

1. The React frontend sends the question to the FastAPI backend.
2. The backend loads the conversation history when necessary.
3. LangGraph processes the question.
4. If the question depends on previous messages, the agent rewrites it to make it clearer.
5. The system searches ChromaDB for related information.
6. Ollama uses the retrieved information to generate an answer.
7. The answer is saved in the conversation and displayed in the frontend.

The general flow is:

```text
User
 |
 v
React Frontend
 |
 v
FastAPI Backend
 |
 v
LangGraph Agent
 |
 +--> Check Conversation History
 |
 +--> Search Documents in ChromaDB
 |
 +--> Generate Answer with Ollama
 |
 v
Save Conversation
 |
 v
Show Answer to User
```

### LangGraph Agent

I divided the agent into three main steps:

**`rewrite_question`**

Checks the conversation history and rewrites follow-up questions when needed.

For example, if the user asks "Who is Edward Cullen?" and then asks "What is his ability?", the agent can understand that the second question is still about Edward.

**`retrieve_documents`**

Searches the vector database for information related to the question.

The retriever currently uses `TOP_K = 3`, meaning it retrieves up to three relevant document fragments.

**`answer_question`**

Uses the retrieved information to generate an answer with Ollama.

When there is not enough information, the chatbot can respond with:

> I don't have enough information to answer that question.

## Document Management

One of the main features of Twilight AI is that administrators can add new information without changing the chatbot's code.

Administrators can upload TXT documents containing information about characters, clans, or events.

When a document is uploaded, the application:

1. Checks that it is a valid TXT file.
2. Verifies that it does not exceed 1 MB.
3. Checks whether the same content has already been uploaded.
4. Divides the text into smaller fragments.
5. Creates embeddings for those fragments.
6. Saves the information in ChromaDB.

The documents are divided into chunks of 500 characters with an overlap of 100 characters.

For embeddings, I used `sentence-transformers/all-MiniLM-L6-v2`.

Administrators can also delete uploaded documents. When this happens, the corresponding information is removed from the vector database.

## Users and Authentication

The application has two types of users.

### Regular User

A regular user can:

- Register and log in.
- Ask questions in the chatbot.
- View their conversation history.
- Continue previous conversations.

### Administrator

An administrator can do everything a regular user can, but also has access to document management.

Administrators can:

- Upload TXT documents.
- View uploaded documents.
- Delete documents.

I used JWT authentication to protect the application endpoints and verify user permissions.

## Project Structure

```text
twilight-ai/
├── backend/
│   ├── agents/
│   ├── auth/
│   ├── database/
│   ├── services/
│   ├── vectorstore/
│   └── main.py
│
├── documents/
│   └── uploads/
│
├── frontend/
│   ├── src/
│   └── package.json
│
├── tests/
│
├── pyproject.toml
└── README.md
```

The main folders are:

- **`backend/agents/`:** Contains the LangGraph agent.
- **`backend/auth/`:** Handles authentication and permissions.
- **`backend/database/`:** Contains the database configuration and models.
- **`backend/services/`:** Handles document management and other application services.
- **`backend/vectorstore/`:** Contains the ChromaDB configuration and document retriever.
- **`documents/`:** Stores the documents used by the chatbot.
- **`frontend/`:** Contains the React application.
- **`tests/`:** Contains the backend tests.

## How to Run the Project

### Requirements

Before running the project, install:

- Python
- uv
- Node.js and npm
- Ollama
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/anah567/twilight-ai.git
cd twilight-ai
```

### 2. Install Backend Dependencies

```bash
uv sync
```

### 3. Download the Ollama Model

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running before starting a conversation.

### 4. Configure the Backend

Create a `.env` file in the project root and add the JWT secret key:

```env
JWT_SECRET_KEY=your_secret_key_here
```

Replace `your_secret_key_here` with a long, randomly generated secret key.

The application uses this key to create and verify JWT tokens. Tokens expire after 30 minutes.

Do not upload the `.env` file to GitHub.

### 5. Start the Backend

From the project root:

```bash
uv run uvicorn backend.main:app --reload
```

The backend runs locally at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs

### 6. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL displayed in the terminal to access the application.

### 7. Add Documents

After setting up an administrator account, upload TXT files from the document-management section.

The chatbot uses the indexed information to answer questions.

### Main API Endpoints

These are the main endpoints used in Twilight AI:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check the API home endpoint |
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in |
| GET | `/auth/me` | Get the current user profile |
| POST | `/chat` | Send a question to the chatbot |
| GET | `/conversations` | Get conversation history |
| GET | `/conversations/{conversation_id}` | Get a specific conversation |
| POST | `/documents/upload` | Upload a TXT document |
| GET | `/documents/` | List uploaded documents |
| DELETE | `/documents/{document_id}` | Delete an uploaded document |

The document-management endpoints are only available to administrators. Other protected endpoints require authentication.

The complete API documentation is available at `http://127.0.0.1:8000/docs` when the backend is running.

## Testing

I used pytest to test different parts of the backend.

To run the tests:

```bash
uv run pytest -q
```

I also tested the chatbot manually using different types of questions.

Some of the tests included:

- Questions about individual characters.
- Questions about vampire covens.
- Questions that require information from different documents.
- Follow-up questions using conversation history.
- Questions about newly uploaded documents.
- Questions that do not have enough information.
- Checking that deleted documents are no longer retrieved.
- Checking administrator permissions.

For example, I tested whether the chatbot could connect information about Carlisle Cullen, the Volturi, and the Cullen family's lifestyle.

I also uploaded new documents and checked whether the chatbot could answer questions using their information.

These tests helped me improve the document retriever and verify that the RAG system was working.

## Example Questions

Some questions that can be asked are:

- Who transformed Edward Cullen into a vampire?
- What is Alice Cullen's special ability?
- Who are the leaders of the Volturi?
- Why did Edward leave Bella in New Moon?
- Why is the Denali coven similar to the Cullen family?
- How did the relationship between the Cullens and the Quileute wolves change?
- How are Alice Cullen's visions, the Denali coven, and the Volturi connected during Breaking Dawn?

The answers depend on the documents available in the knowledge base.

## Notes

The project runs locally and uses SQLite and ChromaDB to store information.

Files such as `.env`, `twilight.db`, `chroma_db/`, and uploaded documents should not be committed to GitHub.

Twilight AI is an academic project, so additional configuration and security improvements would be needed before deploying it as a production application.

## Project Status

The main application is working locally.

So far, I have implemented the backend, RAG agent, document retrieval, authentication, conversation history, document management, and React frontend.

I have also tested the chatbot with simple and more complex questions to check how it retrieves and connects information from different documents.

