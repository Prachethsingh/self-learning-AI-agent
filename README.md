# Self‑Learning AI Agent – Complete Project

![Hero Banner](https://pub-940ccf6255b54fa799a9b01050e6c227.r2.dev/gradients/hero_gradient/hero-gradients-01.png)

A **self‑learning AI agent** that can observe, think, act, evaluate, learn, remember and improve over time.  It ships with a full‑stack backend (FastAPI, PostgreSQL, Redis, Qdrant) and a modern React 18 dashboard built with **TypeScript**, **Tailwind CSS**, and **shadcn/ui** components.

---

## 📦 What’s Inside?

| Layer | Tech | Why |
|------|------|-----|
| **Backend** | Python 3.11+, FastAPI, LangGraph, PostgreSQL, Redis, Qdrant, Docker | Provides a robust, scalable API with memory, tools, and a learning loop |
| **Frontend** | React 18, TypeScript, Tailwind CSS, shadcn/ui, Recharts | Interactive dashboard with real‑time updates via WebSocket |
| **LLM** | OpenAI (GPT‑4/4o) **or** Anthropic (Claude 3) | Core brain for reasoning, planning and generation |
| **Search** | DuckDuckGo, SearX (fallback), optional Brave/Google APIs | Free, privacy‑first web search capabilities |
| **Audio** | Web Audio API + SpeechRecognition (fallback simulated) | Voice input for the chat component |

---

## 🚀 Quick‑Start Guide

> **Prerequisites**: Docker Desktop, Node ≥ 18, Python ≥ 3.11, git.

### 1. Clone & Initialise

```bash
git clone https://github.com/yourusername/self-learning-agent.git
cd self-learning-agent
```

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env – set your OpenAI / Anthropic keys, DB passwords, etc.
```

### 3. Start the backend services (Docker Compose)

```bash
docker‑compose up -d postgres redis qdrant
# Verify they're up:
docker‑compose ps
```

### 4. Install Python dependencies & run the API

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload   # http://localhost:8000
```

### 5. Front‑end – React dashboard

```bash
cd frontend
npm install          # installs React, Tailwind, shadcn‑ui, etc.
npm start              # launches http://localhost:3000
```

### 6. Verify everything works

- **API health**: `curl http://localhost:8000/health`
- **Dashboard**: Open `http://localhost:3000` – you should see the **Agent Dashboard**, **Task Queue**, **Memory Viewer**, and **Learning Progress** panels.
- **WebSocket**: Real‑time updates appear as you interact with the agent (e.g., submit a prompt).

---

## 🛠️ Development Workflow

| Action | Command |
|--------|---------|
| Run tests | `pytest` |
| Lint / format | `black . && flake8 . && mypy .` |
| Re‑generate shadcn UI component | `npx shadcn-ui@latest add <component>` |
| Watch backend changes (auto‑reload) | `uvicorn api.main:app --reload` |
| Watch frontend changes | `npm start` |

---

## 📂 Project Layout

```text
self-learning-agent/
├─ api/                 # FastAPI app (router, middleware, security)
│   ├─ main.py
│   └─ routes/          # agent, memory, tasks endpoints
├─ agent/               # Brain, Planner, Executor, Evaluator, Learner
├─ memory/              # Short‑term, Long‑term (Postgres), Vector (Qdrant)
├─ tools/               # web_search, python_tool, filesystem, database, git
├─ database/            # SQLAlchemy models & Pydantic schemas
├─ frontend/            # React dashboard (TS, Tailwind, shadcn/ui)
│   ├─ src/
│   │   ├─ components/  # UI components (AgentDashboard, TaskQueue…)
│   │   ├─ components/ui/  # **shadcn‑style** folder – ImageStreamHero, demos, etc.
│   │   ├─ hooks/       # useWebSocket hook
│   │   └─ App.tsx
│   └─ public/
├─ docker/               # Dockerfiles for API & Frontend
├─ tests/               # Backend & frontend test suites
└─ docs/                # Additional documentation, diagrams
```

> **Why `/components/ui`?**  shadcn UI conventions place reusable UI primitives in a dedicated `ui` sub‑folder. It keeps the component hierarchy tidy and allows the `ui` folder to be imported as `@/components/ui/...` throughout the app.

---

## 🎨 Demo Screenshots (embedded images)

| Dashboard | Image Stream Hero |
|---|---|
| ![Dashboard](https://pub-940ccf6255b54fa799a9b01050e6c227.r2.dev/gradients/hero_gradient/hero-gradients-01.png) | ![Hero](https://pub-940ccf6255b54fa799a9b01050e6c227.r2.dev/stock-images/767d99bb371a54d0d36751e8cecae43c.jpg) |
| **Task Queue** – real‑time updates | **Chat Input** – voice + attachment UI |
| ![Task Queue](https://pub-940ccf6255b54fa799a9b01050e6c227.r2.dev/gradients/crimson_aura/crimson-aura-02.png) | ![Chat Input](https://pub-940ccf6255b54fa799a9b01050e6c227.r2.dev/gradients/hue-flow/hue-flow-01.png) |

---

## 📚 Learning Loop & Memory

1. **Observe** – Agent receives a task via the API.
2. **Think** – `Brain` (LLM) generates a plan via `Planner`.
3. **Act** – `Executor` runs tools (search, file ops, DB, git).
4. **Evaluate** – `Evaluator` scores the result, returns feedback.
5. **Learn** – `Learner` stores the experience in vector memory (Qdrant) and long‑term relational memory (Postgres).
6. **Repeat** – Future tasks benefit from the stored experiences.

---

## 🗂️ Adding New Components (shadcn style)

```bash
# From the project root
npx shadcn-ui@latest add button   # example – adds to src/components/ui
```

All UI components should live under `src/components/ui`.  Export them via an `index.ts` if you want barrel imports:

```ts
// src/components/ui/index.ts
export { default as ImageStreamHero } from './image-stream-hero';
export { default as DemoOne } from './demo';
```

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch (`git checkout -b feat/awesome‑feature`).
3. Ensure tests pass (`pytest`).
4. Submit a pull request.

---

## 📜 License

MIT – see `LICENSE` file.

---

## 🙋‍♀️ Need Help?

- **Discord**: `#self‑learning‑ai` in the community server.
- **Issues**: Open a GitHub issue with a minimal reproduction.
- **Docs**: Additional diagrams are in `docs/architecture.mermaid` (view with Mermaid live editor).

Enjoy building smarter agents! 🚀