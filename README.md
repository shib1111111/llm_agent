# Agentic Chatbot

The **Agentic Chatbot** is a FastAPI-based backend service designed for secure user authentication, document management, and intelligent query processing. It supports role-based access control, PDF document uploads, and advanced query handling using a combination of database and document-based search. Integrated with a PostgreSQL database and vector stores for document querying, it powers applications requiring robust user management and data processing. The source code is available at [https://github.com/shib1111111/llm_agent](https://github.com/shib1111111/llm_agent).

The server runs on `localhost:8080`, and the client is a Vite-based Vue.js application with TypeScript and TSX, running on `localhost:5173`.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Schema](#database-schema)
- [Document Processing](#document-processing)
- [Security](#security)
- [Video Guides](#video-guides)
- [License](#license)
- [Contact](#Contact)

## Features
- **Secure User Authentication**:
  - User signup with unique username, email, and role validation.
  - Login with OAuth2 and JWT token generation (30-minute expiration).
  - Logout functionality to expire active sessions.
- **Role-Based Access Control**:
  - Restricts document uploads and queries to user-specific roles (e.g., admin, user, guest).
  - Configurable roles and associated default documents via `ROLE_PDFS`.
- **Document Management**:
  - Upload and process PDF documents, stored in role-specific directories (`ROOT_DIR/dataset/pdfs/<role>`).
  - Support for default documents per role, processed on startup.
  - Vector store creation for efficient document querying.
- **Advanced Query Processing**:
  - **Agent Queries**: Combines database and document data for comprehensive responses using `QueryAgent`.
  - **Document Queries**: Searches role-specific PDF documents via `DocumentQuery`.
  - **Database Queries**: Executes SQL queries on PostgreSQL with natural language responses via `DatabaseQuery`.
- **Session and Activity Logging**:
  - Tracks user sessions with `UserSession` (session ID, token, expiration).
  - Logs detailed system information on login (client IP, MAC address, OS, browser, device, memory, CPU cores).
  - Stores query history with processing times in `ChatHistory`.
- **Database Integration**:
  - PostgreSQL backend with SQLAlchemy ORM for robust data management.
  - Schema retrieval and query execution via `DatabaseManager`.
- **CORS Support**:
  - Configured for secure communication with the Vite Vue frontend (`localhost:5173`).
- **Comprehensive Logging**:
  - Detailed logs for debugging, excluding sensitive data (e.g., API keys, JWT secrets).
- **Timezone Awareness**:
  - All timestamps use `Asia/Kolkata` timezone, with migration support for offset-naive data.
- **Scalable Architecture**:
  - Modular design with separate authentication, API, and utility modules.
  - Extensible for additional LLM integrations (e.g., Groq, Anthropic).

## Architecture
The application follows a modular architecture:
- **FastAPI Framework**: Handles HTTP requests and routing (`app.py`).
- **SQLAlchemy ORM**: Manages PostgreSQL interactions (`models.py`).
- **Document Processor**: Converts PDFs into vector stores (`document_processor.py`).
- **Query Agent**: Integrates database and document queries with LLM support (`llm_agent.py`, `doc_query.py`, `db_query.py`).
- **Authentication**: Implements OAuth2 with JWT tokens (`auth.py`, `api_utils.py`).
- **CORS Middleware**: Ensures secure frontend communication.
- **Configuration**: Centralized via `CONFIG` object (`config.py`).

Key files:
- `app.py`: Application entry point, sets up FastAPI and middleware.
- `auth.py`: Manages user authentication (signup, login, logout).
- `api.py`: Handles core operations (database connection, document upload, queries).
- `api_utils.py`: Provides utilities for authentication, token creation, and system info.
- `config.py`: Defines settings (e.g., `DB_URI`, `JWT_SECRET_KEY`, `ROLE_PDFS`).
- `models.py`: SQLAlchemy models for `User`, `UserSession`, `UserLog`, `Documents`, `ChatHistory`.
- `schema.py`: Pydantic models for request/response validation.

## Prerequisites
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **Node.js**: Compatible with Vite 4.x or higher for the Vue frontend
- **Dependencies**:
  - Python: `fastapi`, `sqlalchemy`, `psutil`, `pyjwt`, `passlib[bcrypt]`, `python-user-agents`, `python-multipart`
  - Node.js: Vite, Vue 3, TypeScript, TSX support
- **Environment**: A `.env` file with configuration settings (see [Configuration](#configuration)).

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/shib1111111/llm_agent
   cd llm_agent
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Frontend**:
   ```bash
   cd frontend
   npm install
   ```

5. **Configure PostgreSQL**:
   - Install PostgreSQL and create a database (e.g., `agentic_chatbot`).
   - Update the `DB_URI` in the `.env` file (see [Configuration](#configuration)).

## Configuration
Create a `.env` file in the project root(server folder) with the following settings:
```env
DB_URI=postgresql://username:password@localhost:5432/agentic_chatbot
JWT_SECRET_KEY=your-secret-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```
Create a `.env` file in the project root (frontend folder) w with the following settings:
```env
VITE_BASE_URL=http://localhost:8080
```
- **DB_URI**: PostgreSQL connection string (updated to use `agentic_chatbot` database).
- **JWT_SECRET_KEY**: Secret key for JWT encoding (generate using `os.urandom(32).hex()`).
- **ROOT_DIR**: Base directory for PDF storage.
- **ALLOWED_ORIGINS**: Frontend URL(s) for CORS (e.g., `http://localhost:5173`).
- **ROLES**: Comma-separated list of valid user roles.
- **ROLE_PDFS**: JSON mapping roles to default PDF documents.
- **GROQ_API_KEY**, **ANTHROPIC_API_KEY**: API keys for LLM services (if used).

## Running the Application
1. **Start the Backend**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080
   ```
   The API will be available at `http://localhost:8080`.

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   The Vue app will run on `http://localhost:5173`.

3. **Database Migration**:
   - Ensure the database schema is created using SQLAlchemy models in `models.py`.
   - Run `migrate_sessions()` (via `api_utils.py`) if `UserSession.expires_at` values are offset-naive.
   - Default documents in `ROLE_PDFS` are processed on startup.

## Database Schema
The PostgreSQL database includes:
- **User**: Stores user details (`id`, `email`, `name`, `username`, `password`, `role`, `signup_timestamp`).
- **UserSession**: Tracks sessions (`session_id`, `user_id`, `token`, `created_at`, `expires_at`, `status`).
- **UserLog**: Logs login details (`user_id`, `client_ip`, `mac_address`, `os_info`, `browser`, `device`, `user_agent`, `memory_gb`, `cpu_cores`, `login_timestamp`).
- **Documents**: Records documents (`user_id`, `filename`, `role`, `file_path`, `doc_type`, `timestamp`).
- **ChatHistory**: Stores query history (`user_id`, `query`, `response`, `response_id`, `query_type`, `query_processing_time`, `chat_timestamp`).

## Document Processing
- **Default Documents**: Defined in `ROLE_PDFS`, processed on startup, stored in `Documents` with `doc_type="default"`.
- **Uploaded Documents**: Stored in `ROOT_DIR/dataset/pdfs/<role>`, recorded with `doc_type="uploaded"`, and processed into vector stores.
- **Vector Store**: Managed by `DocumentProcessor` for efficient document queries via `DocumentQuery`.

## Security
- **JWT Authentication**: Validates tokens for protected endpoints using `OAuth2PasswordBearer`.
- **Password Hashing**: Uses bcrypt via `passlib` for secure password storage.
- **CORS**: Restricted to `ALLOWED_ORIGINS` (e.g., `http://localhost:5173`).
- **Session Management**: Tokens expire after 30 minutes; expired sessions are cleaned up on startup.
- **Timezone Handling**: All timestamps use `Asia/Kolkata`; `migrate_sessions()` ensures timezone-aware `UserSession.expires_at`.
- **Logging**: Excludes sensitive data (e.g., `JWT_SECRET_KEY`, API keys) from logs.

## Video Guides
- **[AI Agent Architecture](https://youtu.be/mWcpJCHRmog?si=I1uqPNXPkHcDNKFK)**:
  - Explains the query agent's architecture, integrating database and document processing.
- **[AI Agent Demo](https://youtu.be/E_-fb--rXds?si=IYtOAuJ0Anl0NqUI)**:
  - Demonstrates signup, login, document upload, and query execution via the Vue frontend.



## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, collaborations, or further details, please reach out:
- **Name:** Shib Kumar  
- **Email:** [shibkumarsaraf05@gmail.com](mailto:shibkumarsaraf05@gmail.com)  
- **GitHub:** [@shib1111111](https://github.com/shib1111111)
