# Atlas - AI-Driven Memory System

Atlas is an AI-driven memory and client management system that serves as an "organizational brain" for businesses managing multiple client relationships.

## Features

- 🧠 **AI Memory System**: Store and retrieve institutional knowledge using vector embeddings
- 👥 **Client Management**: Organize clients with ownership structures and strategic planning
- 💬 **Conversations**: Track conversations and interactions with semantic analysis
- 📊 **Strategic Planning**: Develop and track strategic plans with AI-assisted insights
- 📝 **Execution Tracking**: Monitor execution with AI-generated summaries
- 🔍 **Semantic Search**: Find relevant memories using vector similarity

## Tech Stack

- **FastAPI**: High-performance API framework for Python
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database with pgvector extension for vector search
- **OpenAI**: AI services for embeddings and analysis
- **JWT Authentication**: Secure authentication system

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-org/atlas.git
cd atlas
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create environment file**

Create a `.env` file in the root directory with the following content:

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/atlas
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
```

5. **Run the application**

```bash
uvicorn main:app --reload
```

### API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Schema

- **owners**: Users who manage clients
- **clients**: Organizations being managed
- **memories**: Institutional knowledge with vector embeddings
- **conversations**: Client interactions with semantic analysis
- **strategic_plans**: Strategic planning documents
- **execution_logs**: Execution tracking with AI analysis
- **tasks**: Task management and tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details. 