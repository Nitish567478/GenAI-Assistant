# Pro GenAI Assistant with RAG

A production-grade, Retrieval-Augmented Generation (RAG) Chat Assistant with a modern, ChatGPT-inspired user interface. This assistant uses vector similarity search to answer questions grounded in a local knowledge base while maintaining high-quality general intelligence.

## 🌟 Key Features

- **Modern Pro UI/UX**: Dark-themed, sidebar-based interface with persistent session history.
- **Advanced RAG Pipeline**: Uses Google `gemini-embedding-001` and FAISS for sub-second document retrieval and grounding.
- **Dual-Intelligence**: Balanced to prioritize local knowledge (`docs.json`) for specific queries while utilizing Gemini's internal knowledge for coding and general small talk.
- **Session Management**: Full chat history support with the ability to create, switch, and delete chat sessions.
- **Interactive UI**: Built-in emoji picker, auto-scrolling, and "typing" indicators.
- **FastAPI Power**: High-performance backend with robust error handling and REST-based LLM transport.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **AI Models**: 
  - Embeddings: `models/gemini-embedding-001`
  - Chat/LLM: `models/gemini-flash-latest` (Gemini 1.5 Flash)
- **Frontend**: Vanilla HTML5, Modern CSS3 (CSS Variables, Flexbox), JavaScript (ES6+)
- **Storage**: Browser LocalStorage for persistent sessions.

## 📁 Project Structure

```text
rag-assistant/
├── app/
│   ├── models/        # Pydantic data schemas
│   ├── routes/        # FastAPI API endpoints
│   ├── services/      # RAG, LLM, and Embedding logic
│   ├── utils/         # Config and Settings
│   ├── vectorstore/   # FAISS Vector Store implementation
│   └── main.py        # Application entry point
├── frontend/          # Modern UI implementation
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docs.json          # Your Knowledge Base
├── requirements.txt   # Python dependencies
├── .env.example       # API Key template
└── README.md          # Comprehensive documentation
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed.
- A Google Gemini API Key (Get one for free at [aistudio.google.com](https://aistudio.google.com/app/apikey)).

### 2. Installation
```bash
# Navigate to project
cd "New folder (2)"

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Commend
python -m app.main
```

### 3. Configuration
1. Rename `.env.example` to `.env`.
2. Open `.env` and paste your API key:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 4. Launch
```bash
python -m app.main
```
The application will start at **`http://localhost:8000`**.

## 🧠 Architecture Explanation

### RAG Workflow
1. **Indexing**: On startup, the `docs.json` file is chunked and converted into 768-dimensional vectors. These are stored in an In-Memory FAISS index.
2. **Querying**: Every user message is converted into a vector.
3. **Retrieval**: FAISS identifies relevant document chunks using **Normalized Inner Product** (equivalent to Cosine Similarity).
4. **Generation**: The retrieved context is injected into a specialized prompt alongside the conversation history, allowing the LLM to generate a grounded, contextual response.

---
*Developed as a Production-Grade GenAI Showcase.*
