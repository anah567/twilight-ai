# Twilight AI 

Twilight AI is a chatbot based on the *Twilight* saga by Stephenie Meyer. I developed this project to create an assistant that can answer questions about the characters, vampire covens, relationships, and events from the story.

The application uses **Retrieval-Augmented Generation (RAG)**, which means the chatbot searches for information in uploaded documents before generating an answer. This helps the chatbot respond using the information available in the project instead of relying only on the language model's general knowledge.

I used **React** for the frontend, **FastAPI** for the backend, **LangGraph** to organize the chatbot's workflow, **Groq** to generate AI responses, and **ChromaDB** to store and search document information.

The application is deployed using **Vercel** for the frontend and **Railway** for the backend.

## Live Application

- **Frontend:** https://twilight-ai.vercel.app
- **Backend:** https://twilight-ai-production.up.railway.app
- **API Documentation:** https://twilight-ai-production.up.railway.app/docs
- **GitHub Repository:** https://github.com/anah567/twilight-ai

## Features

The application includes:

- A chatbot that answers questions about the Twilight saga.
- A RAG system that searches uploaded documents before answering.
- Conversation history so users can continue previous chats.
- User registration and login.
- JWT authentication.
- Two user roles: regular user and administrator.
- A document section where administrators can upload, view, and delete TXT files.
- Duplicate document validation.
- A React interface inspired by the Twilight aesthetic.
- Persistent storage for users, conversations, and document embeddings.
- Cloud deployment using Vercel and Railway.

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
| Groq | Running the language model through a cloud API |
| GPT-OSS 20B | Language model used through Groq |
| ChromaDB | Storing and searching document embeddings |
| Hugging Face Embeddings | Converting text into vectors |
| SQLite | Storing users, conversations, and document records |
| JWT | User authentication |
| SQLAlchemy | Database operations |
| pytest | Backend testing |
| Docker | Packaging the backend application |
| Railway | Backend hosting and persistent storage |
| Vercel | Frontend hosting |
| GitHub | Version control |

## How the Chatbot Works

When a user sends a question, the application follows these steps:

1. The React frontend sends the question to the FastAPI backend.
2. The backend loads the conversation history when necessary.
3. LangGraph processes the question.
4. If the question depends on previous messages, the agent rewrites it to make it clearer.
5. The system searches ChromaDB for related information.
6. Groq uses the retrieved information to generate an answer.
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
  +--> Rewrite Question (if needed)
  |
  +--> Search Documents in ChromaDB
  |
  +--> Generate Answer with Groq
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

The retriever uses a configurable number of relevant document fragments to provide context for the answer.

**`answer_question`**

Uses the retrieved information to generate an answer with Groq.

The language model is configured using `ChatGroq`, with the model `openai/gpt-oss-20b`.

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
7. Registers the document in the database.

The documents are divided into chunks of 500 characters with an overlap of 100 characters.

For embeddings, I used `sentence-transformers/all-MiniLM-L6-v2`.

Administrators can also delete uploaded documents. When this happens, the corresponding information is removed from the vector database.

### Uploaded Documents

The application has been tested with documents about:

- Bella Swan
- Edward Cullen
- Alice Cullen

Additional documents can be uploaded by administrators to expand the chatbot's knowledge.

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

The backend checks administrator permissions before allowing document uploads or deletions.

### Security Validation

I tested the application using an administrator account and a regular user account.

The regular user could access the chatbot but could not access the document-management section.

I also tested the protected endpoints directly using Swagger.

When the regular user attempted to upload or delete documents, the API rejected the request with:

```text
403 Forbidden
Administrator permissions required.
```

This confirms that administrator permissions are checked by the backend, not only by the frontend.

## Project Structure

```text
twilight-ai/
├── backend/
│   ├── agents/
│   ├── auth/
│   ├── database/
│   ├── services/
│   ├── vectorstore/
│   ├── Dockerfile
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
├── uv.lock
├── railway.json
└── README.md
```

The main folders are:

- **`backend/agents/`:** Contains the LangGraph agent and language model configuration.
- **`backend/auth/`:** Handles authentication and permissions.
- **`backend/database/`:** Contains the database configuration and models.
- **`backend/services/`:** Handles document management and other application services.
- **`backend/vectorstore/`:** Contains the ChromaDB configuration and document retriever.
- **`documents/`:** Contains document-related files.
- **`frontend/`:** Contains the React application.
- **`tests/`:** Contains backend tests.

## How to Run the Project Locally

### Requirements

Before running the project, install:

- Python 3.13
- uv
- Node.js and npm
- Git

You also need a Groq API key to use the language model.

### 1. Clone the Repository

```bash
git clone https://github.com/anah567/twilight-ai.git
cd twilight-ai
```

### 2. Install Backend Dependencies

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root.

Add the required configuration:

```env
JWT_SECRET_KEY=your_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./twilight.db
CHROMA_DB_PATH=./chroma_db
```

Replace the example values with your own credentials.

The JWT secret is used to create and verify authentication tokens.

The Groq API key allows the backend to communicate with the language model.

The database paths determine where SQLite and ChromaDB store their information.

**Important:** Never upload the `.env` file or real API keys to GitHub.

### 4. Start the Backend

From the project root:

```bash
uv run uvicorn backend.main:app --reload
```

The backend runs locally at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs

Make sure the required environment variables are available to the backend process.

### 5. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
```

Create a `.env` file inside the `frontend` folder with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Then run:

```bash
npm run dev
```

Open the URL displayed in the terminal to access the application.

### 6. Add Documents

After setting up an administrator account, upload TXT files from the document-management section.

The chatbot uses the indexed information to answer questions.

## Cloud Deployment

Twilight AI is deployed using two cloud platforms.

### Frontend: Vercel

The React application is hosted on Vercel.

Vercel builds the frontend and makes it available through a public URL.

The frontend communicates with the Railway backend through HTTP requests.

The deployed frontend uses the environment variable:

```env
VITE_API_URL=https://twilight-ai-production.up.railway.app
```

### Backend: Railway

The FastAPI application is hosted on Railway.

Railway runs the backend using Docker and makes the API available through a public URL.

The backend uses environment variables to configure authentication, the language model, and persistent storage.

The main Railway environment variables are:

```env
JWT_SECRET_KEY=your_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:////data/twilight.db
CHROMA_DB_PATH=/data/chroma_db
FRONTEND_URL=https://twilight-ai.vercel.app
```

These are example values. Real credentials must be configured privately in Railway.

### Docker

The backend includes a Dockerfile that:

1. Uses Python 3.13.
2. Installs uv.
3. Installs the project dependencies.
4. Copies the backend source code.
5. Starts the FastAPI application using Uvicorn.

Docker helps Railway run the backend in a consistent environment.

### Persistent Storage

Railway containers can lose locally stored files when they are replaced during a deployment.

To prevent this, I configured a persistent Railway Volume mounted at:

```text
/data
```

The application stores its databases inside this volume:

| Data | Storage Location |
|---|---|
| Users | `/data/twilight.db` |
| Conversations | `/data/twilight.db` |
| Document records | `/data/twilight.db` |
| Document embeddings | `/data/chroma_db` |

This allows SQLite and ChromaDB to keep their data across application redeployments while the volume remains attached.

### Persistence Testing

I tested the persistent storage by redeploying the backend.

After the deployment:

- The administrator account was still registered.
- Administrator permissions were preserved.
- Previous conversations remained available.
- Uploaded document records were still visible.
- ChromaDB files remained stored in the persistent volume.
- The `twilight_knowledge` collection could still be opened and queried.

I also verified that the chatbot continued answering questions after the deployment.

## Main API Endpoints

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

Document-management operations require administrator permissions. Other protected endpoints require authentication.

The complete API documentation is available at:

https://twilight-ai-production.up.railway.app/docs

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
- Checking administrator permissions.
- Checking persistent storage after redeployment.
- Testing the frontend and backend together.

### Chatbot Tests

I tested questions such as:

**Question:**

Who is Alice Cullen, and what is her special ability?

**Expected behavior:**

The chatbot should explain that Alice Cullen is a vampire and that she can see possible future events.

**Question:**

Who is Edward Cullen?

**Expected behavior:**

The chatbot should explain Edward's role in the Twilight saga and describe his abilities and relationships.

### Insufficient Information Test

I also tested questions that were not supported by the uploaded documents.

For example:

What is the exact name of Bella Swan's mathematics teacher in Phoenix?

When there is not enough information, the chatbot should respond with:

> I don't have enough information to answer that question.

This helps reduce unsupported answers.

### Authentication and Authorization Tests

I tested two different accounts:

- An administrator who could manage documents.
- A regular user who could use the chatbot but could not upload or delete documents.

The API returned `403 Forbidden` when the regular user attempted administrative operations.

### Persistence Tests

I redeployed the Railway backend and verified that:

- User accounts were preserved.
- Conversations were preserved.
- Administrator permissions remained active.
- Uploaded documents were still registered.
- ChromaDB remained available.

These tests helped me verify that the deployed application continued working after a backend restart or redeployment.

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

Twilight AI is an academic project developed to practice backend development, frontend development, artificial intelligence, RAG, authentication, and cloud deployment.

The application uses SQLite and ChromaDB to store information.

Sensitive or generated files such as `.env`, `twilight.db`, `chroma_db/`, and private uploaded documents should not be committed to GitHub.

The application uses persistent cloud storage, but additional improvements such as automated backups, monitoring, and stronger production security would be useful for a larger deployment.

## Project Status

Twilight AI is deployed and its main features are working.

The application includes:

- A React frontend deployed on Vercel.
- A FastAPI backend deployed on Railway.
- A LangGraph agent connected to Groq.
- A RAG system using ChromaDB.
- User registration and JWT authentication.
- Regular user and administrator roles.
- Conversation history.
- Document upload, listing, and deletion.
- Persistent storage for SQLite and ChromaDB.
- Protected administrator endpoints.

I tested the chatbot with simple and complex questions, checked user permissions, and verified that the application's data remained available after redeployment.

The project demonstrates how a full-stack application can combine artificial intelligence, document retrieval, databases, authentication, and cloud services.