# Enhanced Self-Learning AI Agent - Complete Setup Guide

This guide covers the enhanced version with all free/open-source components, security features, real-time updates, and production readiness.

## 🚀 Quick Start (Production Ready)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- (Optional) API keys for enhanced search: Brave Search, Google Programmable Search

### 1. Clone & Setup
```bash
git clone <repository-url>
cd self-learning-agent
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration:
# OPENAI_API_KEY=your_openai_key (required for LLM)
# BRAVE_SEARCH_API_KEY=your_brave_key (optional, for enhanced search)
# GOOGLE_SEARCH_API_KEY=your_google_key (optional, requires custom search engine)
# SECRET_KEY=your_secret_key_here (for JWT tokens in production)
```

### 3. Start All Services
```bash
# Using Docker Compose (includes all services)
docker-compose up -d

# Verify everything is running:
docker-compose ps
```

Expected services:
- **api**: Self-learning agent API (port 8000)
- **frontend**: React dashboard (port 3000) 
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **qdrant**: Vector search engine (port 6333)

### 4. Access Your Agent
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (interactive testing)
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws (real-time updates)

## 🔧 Enhanced Features Included

### ✅ Security & Authentication
- JWT-based authentication (simplified for demo, production-ready)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Rate limiting (100 requests/minute per IP)
- Input validation and sanitization
- CORS configuration

### ✅ Free Search Engines (Multiple Fallbacks)
1. **DuckDuckGo** (Primary - no API key required)
2. **SearX** (Meta-search - multiple public instances)
3. **Brave Search** (Requires free API key, 2000 queries/month free)
4. **Google Programmable Search** (Requires API key + custom search engine)
5. **Educational Placeholders** (When all search fails)

### ✅ Real-Time Capabilities
- WebSocket connection for live updates
- Automatic fallback to polling if WebSocket fails
- Live dashboard updates for:
  - Agent status changes
  - Task completion events
  - Memory system updates
  - Learning progress metrics

### ✅ Enhanced Monitoring
- Detailed health checks for all components
- Memory usage statistics
- Learning metrics visualization
- Task execution tracking
- Performance monitoring

### ✅ Development Experience
- Hot reloading for frontend changes
- Automatic API reload on code changes
- Comprehensive logging
- Error boundaries and graceful degradation
- Complete API documentation (Swagger/OpenAPI)

## 📊 Architecture Overview

```
Frontend (React 18) 
    ↓ WebSocket / REST API
API Layer (FastAPI) 
    ↓
Agent Core: Brain → Planner → Executor → Evaluator → Learner
    ↓           ↓           ↓           ↓           ↓
Memory Systems: Short-term ↔ Long-term ↔ Vector Memory
    ↓           ↓           ↓
Tools Ecosystem: Web Search → Python → Filesystem → Database → Git
    ↓           ↓           ↓           ↓           ↓
Services: PostgreSQL → Redis → Qdrant → (External APIs)
```

## 🔐 Security Details

### Authentication (Production Ready)
The system includes JWT authentication framework:
- Login endpoint: `POST /api/auth/login`
- Token refresh: `POST /api/auth/refresh`
- Protected routes: All API endpoints require valid token
- Role-based access control (extendable)

For demo purposes, the system accepts any token or creates a demo user. In production:
1. Set `SECRET_KEY` in .env (use `openssl rand -hex 32`)
2. Implement proper user registration/login
3. Connect to actual user database

### Rate Limiting
- 100 requests per minute per IP address
- Applies to all `/api/` endpoints
- Returns 429 status when limit exceeded
- Header information available for monitoring

### Security Headers Applied
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 🔍 Search Engine Configuration

### Free Tier Limits
| Engine | Free Tier | Setup Required | Notes |
|--------|-----------|----------------|-------|
| DuckDuckGo | Unlimited | None | Primary fallback |
| SearX | Unlimited | None | Uses public instances |
| Brave | 2000/month | API key | Good quality results |
| Google Programmable | 100/day | API key + CX ID | Most familiar results |

To enable enhanced search:
1. Get free API keys from:
   - Brave: https://brave.com/search/api/
   - Google: https://developers.google.com/custom-search/v1/overview
2. Add to .env:
   ```
   BRAVE_SEARCH_APIKEY=your_key_here
   GOOGLE_SEARCH_APIKEY=your_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_cx_id_here
   ```

## 🐳 Docker Compose Services Explained

### api
- Builds from Dockerfile.api
- Mounts code for live development
- Exposes port 8000
- Depends on: postgres, redis, qdrant
- Environment: All from .env file

### frontend  
- Builds from Dockerfile.frontend
- Exposes port 3000
- Mounts code for live development
- Environment: REACT_APP_API_URL=http://localhost:8000

### postgres
- Official PostgreSQL 15-alpine image
- Pre-configured database: self_learning_agent
- Persistent volume: postgres_data

### redis
- Official Redis 7-alpine image
- Persistent volume: redis_data

### qdrant
- Official Qdrant v1.6.1 image
- Exposes both REST (6333) and gRPC (6334) ports
- Persistent volume: qdrant_data

## 📈 Monitoring & Observability

### Health Checks
- `/health` endpoint returns status of all components
- Component-level reporting (brain, planner, memory, tools, etc.)
- Timestamp for freshness verification
- Error details when unhealthy

### Metrics Available
Through API endpoints:
- `GET /api/agent/status` - Complete agent state + learning stats
- `GET /api/memory/stats` - Detailed memory system metrics
- `GET /api/tasks/stats` - Task queue performance
- WebSocket broadcasts - Real-time updates

### Logging
- Structured logging with timestamps
- Configurable log levels (INFO by default)
- Error tracking with stack traces
- Request/response logging for debugging

## 🛠️ Development Workflow

### Making Changes
1. **Backend API Changes**:
   - Edit files in `/api/`
   - Auto-reloads via Docker volume mount
   - Check logs: `docker-compose logs -f api`

2. **Frontend Changes**:
   - Edit files in `/frontend/src/`
   - Hot reloads via Docker volume mount
   - Check: http://localhost:3000

3. **Adding New Tools**:
   - Create file in `/tools/`
   - Register in `api/main.py` tools dictionary
   - Update imports and executor initialization

4. **Database Changes**:
   - Modify models in `/database/`
   - Create migration: `alembic revision --autogenerate`
   - Apply: `alembic upgrade head`

### Testing
```bash
# Backend tests
pytest api/

# Frontend tests (when added)
cd frontend && npm test

# Full test suite
pytest
```

## 🚨 Troubleshooting

### Common Issues

#### "WebSocket connection failed"
- Check if API is running on port 8000
- Verify no firewall blocking ws://localhost:8000/ws
- Dashboard automatically falls back to polling

#### "Database connection failed"
- Verify postgres service is running: `docker-compose ps`
- Check .env DATABASE_URL format
- Try manual connection: `psql postgresql://user:password@localhost:5432/self_learning_agent`

#### "Search not working"
- Check API logs for search engine errors
- Verify internet connectivity
- Try different search terms
- Remember: educational placeholders appear when all engines fail

#### "High memory usage"
- Qdrant and Redis can be memory intensive
- Consider reducing vector dimensions in production
- Monitor with: `docker stats`

## 📚 Next Steps After Setup

### 1. Run Example Tasks
Check `EXAMPLE_TASKS.md` for guided learning sequences

### 2. Explore the API
Visit http://localhost:8000/docs to interactively test all endpoints

### 3. Monitor Learning
Watch the dashboard as you run similar tasks and observe:
- Decreasing execution times
- Increasing success rates
- Strategy improvements
- Experience accumulation

### 4. Customize for Your Domain
- Add specialized tools in `/tools/`
- Create domain-specific memory categories
- Configure custom evaluation criteria
- Build specialized frontend components

### 5. Prepare for Production
- Generate strong SECRET_KEY
- Configure proper authentication
- Set up SSL/TLS termination (nginx/apache)
- Set up monitoring and alerting
- Configure backup strategies for PostgreSQL/Qdrant

## 💡 Pro Tips

### Maximizing Learning Efficiency
1. **Task Sequencing**: Run similar tasks back-to-back
2. **Specificity**: Be precise in task descriptions for better pattern matching
3. **Feedback Loop**: Use the learning endpoint to see what the agent retained
4. **Variety**: Mix task types to build broad capabilities
5. **Patience**: True learning emerges after 10-20 similar tasks

### Resource Optimization
- Adjust Qdrant vector size based on your embedding model
- Tune Redis cache sizes based on available memory
- Consider PostgreSQL connection pooling for high concurrency
- Monitor disk usage for long-term memory growth

### Extending Capabilities
- Add OCR tool (tesseract) for image text extraction
- Add speech-to-text/text-to-speech tools
- Add specialized APIs (weather, finance, etc.) as free tiers allow
- Add multi-agent collaboration features
- Implement advanced learning techniques (meta-learning, curriculum learning)

## 📞 Support & Community

If you encounter issues:
1. Check the logs: `docker-compose logs -f [service]`
2. Review this guide and EXAMPLE_TASKS.md
3. Verify all prerequisites are installed correctly
4. Ensure ports 3000, 8000, 5432, 6379, 6333 are available
5. Consider simplifying to minimal setup first, then add components

**Remember**: Your self-learning agent improves with every interaction. The more you use it, the more valuable it becomes as a personalized AI assistant that truly understands your workflow and preferences.

Happy learning! 🧠