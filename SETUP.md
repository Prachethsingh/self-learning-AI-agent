# Self-Learning AI Agent - Setup Guide

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for production deployment)
- OpenAI or Anthropic API key

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd self-learning-agent
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 4. Start the services
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or run services manually
# Start PostgreSQL
docker run -d --name postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=self_learning_agent -p 5432:5432 postgres:15-alpine

# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:v1.6.1

# Start the API
uvicorn api.main:app --reload
```

### 5. Start the frontend
```bash
cd frontend
npm install
npm start
```

The dashboard will be available at `http://localhost:3000`

## API Endpoints

### Agent Endpoints
- `POST /api/agent/execute` - Execute a task
- `GET /api/agent/status` - Get agent status
- `POST /api/agent/reset` - Reset agent state

### Memory Endpoints
- `POST /api/memory/short-term` - Add to short-term memory
- `GET /api/memory/short-term/{session_id}` - Get short-term memory
- `POST /api/memory/long-term` - Add to long-term memory
- `GET /api/memory/long-term` - Get long-term memory
- `POST /api/memory/long-term/search` - Search long-term memory
- `POST /api/memory/vector` - Add to vector memory
- `POST /api/memory/vector/search` - Search vector memory
- `GET /api/memory/stats` - Get memory statistics

### Task Endpoints
- `POST /api/tasks/` - Create a task
- `GET /api/tasks/` - List tasks
- `GET /api/tasks/next` - Get next task
- `PUT /api/tasks/{task_id}/complete` - Complete a task
- `DELETE /api/tasks/{task_id}` - Delete a task
- `GET /api/tasks/stats` - Get task statistics

## Project Structure

```
self-learning-agent/
├── agent/              # Core agent components
│   ├── brain.py       # LLM integration and reasoning
│   ├── planner.py     # Task planning and decomposition
│   ├── executor.py    # Task execution
│   ├── evaluator.py   # Result evaluation
│   └── learner.py     # Learning and memory updates
├── memory/             # Memory systems
│   ├── short_term.py  # Conversation memory
│   ├── long_term.py   # Persistent knowledge
│   ├── vector_memory.py # Vector search
│   └── models.py      # Data models
├── tools/              # Available tools
│   ├── web_search.py  # Web search capabilities
│   ├── python_tool.py # Python execution
│   ├── filesystem.py  # File operations
│   ├── database.py    # Database queries
│   └── git_tool.py    # Git operations
├── api/                # FastAPI application
│   ├── main.py        # Main application
│   └── routes/        # API routes
├── database/           # Database models
├── frontend/           # React dashboard
├── docker/             # Docker configuration
└── tests/              # Test suites
```

## Running Tests

```bash
pytest
```

## Development

### Code Formatting
```bash
black .
flake8 .
mypy .
```

### Database Migrations
```bash
alembic upgrade head
```

## Troubleshooting

### PostgreSQL Connection Issues
Ensure PostgreSQL is running and accessible:
```bash
docker exec -it postgres psql -U user -d self_learning_agent
```

### Redis Connection Issues
Check Redis status:
```bash
docker exec -it redis redis-cli ping
```

### Qdrant Connection Issues
Verify Qdrant is accessible:
```bash
curl http://localhost:6333/health
```

## Production Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### Environment Variables
Set the following in production:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key (if using Claude)
- `DATABASE_URL` - Production database connection
- `REDIS_URL` - Production Redis connection
- `QDRANT_URL` - Production Qdrant connection
- `SECRET_KEY` - Secure secret for JWT tokens

### Security Considerations
- Use HTTPS in production
- Implement proper authentication
- Rate limit API endpoints
- Use environment-specific configuration
- Regular security updates

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review the code comments

## License

MIT License - see LICENSE file for details.