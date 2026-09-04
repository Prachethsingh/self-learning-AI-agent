import React, { useState, useEffect } from 'react';
import useWebSocket from './hooks/useWebSocket';
import AgentDashboard from './components/AgentDashboard';
import TaskQueue from './components/TaskQueue';
import MemoryViewer from './components/MemoryViewer';
import LearningProgress from './components/LearningProgress';
import './App.css';

const SUGGESTED_PROMPTS = [
  "Analyze current memory state and summarize active subsystems",
  "Inspect Git repository commit history and current working branch",
  "Scan local directory structure and summarize key components",
  "Execute a Python benchmark for matrix multiplication algorithms"
];

const FREE_LLM_PRESETS = [
  {
    id: 'autonomous',
    name: '⚡ Built-in Autonomous Engine (100% Free, No Key Required)',
    provider: 'openai',
    model: 'autonomous-heuristic-v1',
    baseUrl: '',
    portalUrl: '',
    keyPlaceholder: 'Leave empty - runs on local tools',
    desc: 'Uses local Python sandbox, Git tools, SQLite, and Vector memory with zero external dependencies.'
  },
  {
    id: 'groq',
    name: '🚀 Groq Cloud (Free & Ultra-Fast GPT-OSS 120B)',
    provider: 'openai',
    model: 'openai/gpt-oss-120b',
    baseUrl: 'https://api.groq.com/openai/v1',
    portalUrl: 'https://console.groq.com/keys',
    keyPlaceholder: 'gsk_...',
    desc: 'Free tier with instant setup and ultra-low latency (< 1s reasoning).'
  },
  {
    id: 'gemini',
    name: '✨ Google Gemini 1.5 Flash (Free Tier)',
    provider: 'openai',
    model: 'gemini-1.5-flash',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    portalUrl: 'https://aistudio.google.com/app/apikey',
    keyPlaceholder: 'AIzaSy...',
    desc: 'Free 1,500 requests/day directly from Google AI Studio without credit card.'
  },
  {
    id: 'openrouter',
    name: '🌐 OpenRouter (Free Tier Models)',
    provider: 'openai',
    model: 'meta-llama/llama-3.3-70b-instruct:free',
    baseUrl: 'https://openrouter.ai/api/v1',
    portalUrl: 'https://openrouter.ai/keys',
    keyPlaceholder: 'sk-or-v1-...',
    desc: 'Access free open-source models with no upfront payment required.'
  },
  {
    id: 'ollama',
    name: '💻 Ollama Local (100% Offline & Private)',
    provider: 'openai',
    model: 'llama3.2',
    baseUrl: 'http://localhost:11434/v1',
    portalUrl: 'https://ollama.com',
    keyPlaceholder: 'Leave empty (not needed for local Ollama)',
    desc: 'Runs completely on your local computer via Ollama.'
  },
  {
    id: 'openai',
    name: '🤖 OpenAI Platform (Official)',
    provider: 'openai',
    model: 'gpt-4o-mini',
    baseUrl: '',
    portalUrl: 'https://platform.openai.com/api-keys',
    keyPlaceholder: 'sk-proj-...',
    desc: 'Official OpenAI GPT models (requires OpenAI account).'
  }
];

const API_BASE = process.env.REACT_APP_API_URL || '';
const WS_BASE = process.env.REACT_APP_WS_URL || (process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL.replace(/^http/, 'ws') + '/ws' : 'ws://localhost:8000/ws');

function App() {
  const [agentStatus, setAgentStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [memoryStats, setMemoryStats] = useState(null);
  const [learningStats, setLearningStats] = useState(null);
  
  // LLM Config state
  const [llmConfig, setLlmConfig] = useState({ provider: 'openai', model: 'gpt-4-turbo-preview', has_api_key: false });
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState('autonomous');
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [providerInput, setProviderInput] = useState('openai');
  const [modelInput, setModelInput] = useState('gpt-4-turbo-preview');
  const [baseUrlInput, setBaseUrlInput] = useState('');
  const [isSavingConfig, setIsSavingConfig] = useState(false);

  // Interactive Agent Console state
  const [prompt, setPrompt] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // WebSocket connection for real-time updates
  const { data: wsData, isConnected: wsConnected } = useWebSocket(WS_BASE);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/agent/config`);
      if (res.ok) {
        const data = await res.json();
        setLlmConfig(data);
        setProviderInput(data.provider || 'openai');
        setModelInput(data.model || 'gpt-4-turbo-preview');
        setBaseUrlInput(data.base_url || '');
      }
    } catch (e) {
      console.warn('Config fetch error:', e);
    }
  };

  const handleSelectPreset = (presetId) => {
    setSelectedPreset(presetId);
    const preset = FREE_LLM_PRESETS.find(p => p.id === presetId);
    if (preset) {
      setProviderInput(preset.provider);
      setModelInput(preset.model);
      setBaseUrlInput(preset.baseUrl);
    }
  };

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setIsSavingConfig(true);
    try {
      const payload = {
        provider: providerInput,
        model: modelInput,
        base_url: baseUrlInput.trim() || null
      };
      if (apiKeyInput.trim()) {
        payload.api_key = apiKeyInput.trim();
      } else if (selectedPreset === 'autonomous' || selectedPreset === 'ollama') {
        payload.api_key = ''; // Clear key for autonomous/local
      }

      const res = await fetch(`${API_BASE}/api/agent/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const updated = await res.json();
        setLlmConfig(updated);
        setApiKeyInput('');
        setShowConfigModal(false);
      }
    } catch (err) {
      alert('Failed to save LLM configuration: ' + err.message);
    } finally {
      setIsSavingConfig(false);
    }
  };

  const fetchAllData = async () => {
    fetchAgentStatus();
    fetchTasks();
    fetchMemoryStats();
    fetchLearningStats();
    fetchConfig();
  };

  useEffect(() => {
    fetchAllData();

    // Handle WebSocket updates
    if (wsData) {
      handleWebSocketUpdate(wsData);
    }

    // Set up interval for fallback updates
    const interval = setInterval(() => {
      fetchAllData();
    }, 8000);

    return () => clearInterval(interval);
  }, [wsData]);

  const handleWebSocketUpdate = (data) => {
    switch (data.type) {
      case 'agent_update':
        setAgentStatus(prev => ({ ...prev, ...data.data }));
        break;
      case 'task_update':
        setTasks(prev => {
          const updatedTasks = prev.map(task =>
            task.id === data.data.id ? data.data : task
          );
          if (!updatedTasks.some(task => task.id === data.data.id)) {
            return [...updatedTasks, data.data];
          }
          return updatedTasks;
        });
        break;
      case 'memory_update':
        setMemoryStats(prev => ({ ...prev, ...data.data }));
        break;
      case 'learning_update':
        setLearningStats(prev => ({ ...prev, ...data.data }));
        break;
      default:
        break;
    }
  };

  const fetchAgentStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agent/status`);
      if (response.ok) {
        const data = await response.json();
        setAgentStatus(data);
        if (data.stats?.learning) {
          setLearningStats(data.stats.learning);
        }
      }
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tasks/`);
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchMemoryStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/memory/stats`);
      if (response.ok) {
        const data = await response.json();
        setMemoryStats(data);
      }
    } catch (error) {
      console.error('Error fetching memory stats:', error);
    }
  };

  const fetchLearningStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agent/status`);
      if (response.ok) {
        const data = await response.json();
        if (data.stats?.learning) {
          setLearningStats(data.stats.learning);
        }
      }
    } catch (error) {
      console.error('Error fetching learning stats:', error);
    }
  };

  // Execute Agent Task
  const handleExecuteTask = async (taskText) => {
    const query = taskText || prompt;
    if (!query.trim() || isExecuting) return;

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/agent/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: query.trim() })
      });

      const data = await response.json();
      if (response.ok) {
        setExecutionResult({
          success: true,
          task: query.trim(),
          ...data
        });
      } else {
        setExecutionResult({
          success: false,
          task: query.trim(),
          error: data.detail || 'Failed to execute task'
        });
      }

      // Refresh memory, tasks, and status
      await fetchAllData();
    } catch (error) {
      setExecutionResult({
        success: false,
        task: query.trim(),
        error: error.message || 'Connection error'
      });
    } finally {
      setIsExecuting(false);
    }
  };

  // Add Task to Pipeline
  const handleAddTask = async (taskData) => {
    const response = await fetch(`${API_BASE}/api/tasks/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData)
    });
    if (response.ok) {
      await fetchTasks();
    }
  };

  // Reset Agent
  const handleResetAgent = async () => {
    if (!window.confirm('Reset agent memory and runtime states?')) return;
    try {
      await fetch(`${API_BASE}/api/agent/reset`, { method: 'POST' });
      await fetchAllData();
      setExecutionResult(null);
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  return (
    <div className="App">
      {/* Sleek Futuristic Header */}
      <header className="App-header">
        <div className="header-brand">
          <div className="brand-icon">⚡</div>
          <div className="brand-info">
            <h1>Self-Learning AI Agent</h1>
            <p>Autonomous Reasoning, Continuous Learning & Memory Synthesis</p>
          </div>
        </div>

        <div className="header-actions">
          <button
            className={`btn-header-action ${llmConfig?.has_api_key ? 'badge-active' : 'badge-neutral'}`}
            onClick={() => setShowConfigModal(true)}
            title="Configure LLM Provider, Model & API Key"
          >
            <span>{llmConfig?.has_api_key ? '🟢' : '⚡'}</span>
            <span>{llmConfig?.has_api_key ? `${llmConfig.model}` : 'Autonomous Mode'}</span>
            <span style={{ fontSize: '0.72rem', opacity: 0.7 }}>⚙️</span>
          </button>

          <span className={`ws-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            <span className="pulse-dot"></span>
            {wsConnected ? 'WebSocket Live' : 'Live Sync Polling'}
          </span>

          <button className="btn-header-action" onClick={fetchAllData} title="Refresh live telemetry">
            <span>🔄</span> Refresh
          </button>
          
          <button className="btn-header-action" onClick={handleResetAgent} title="Reset runtime states" style={{ color: '#fda4af' }}>
            <span>🗑️</span> Reset
          </button>
        </div>
      </header>

      {/* LLM Settings Modal */}
      {showConfigModal && (
        <div className="modal-backdrop" onClick={() => setShowConfigModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '580px' }}>
            <div className="modal-header">
              <h3>⚙️ AI Model & Free API Key Configuration</h3>
              <button className="btn-close" onClick={() => setShowConfigModal(false)}>✕</button>
            </div>

            <form onSubmit={handleSaveConfig} className="task-form">
              <div className="form-group">
                <label>Select AI Engine / Free Provider Preset</label>
                <select
                  value={selectedPreset}
                  onChange={(e) => handleSelectPreset(e.target.value)}
                  className="form-input"
                  style={{ fontWeight: 600, color: 'var(--primary-glow)' }}
                >
                  {FREE_LLM_PRESETS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
                {(() => {
                  const curr = FREE_LLM_PRESETS.find(p => p.id === selectedPreset);
                  if (!curr) return null;
                  return (
                    <div style={{ marginTop: '8px', fontSize: '0.82rem', color: 'var(--text-secondary)', background: 'rgba(255,255,255,0.03)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                      <p style={{ margin: '0 0 6px 0' }}>{curr.desc}</p>
                      {curr.portalUrl && (
                        <a
                          href={curr.portalUrl}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: '#38bdf8', textDecoration: 'underline', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                        >
                          👉 Get your free key here: {curr.portalUrl} ↗
                        </a>
                      )}
                    </div>
                  );
                })()}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label>Provider Type</label>
                  <select
                    value={providerInput}
                    onChange={(e) => setProviderInput(e.target.value)}
                    className="form-input"
                  >
                    <option value="openai">OpenAI / Compatible</option>
                    <option value="anthropic">Anthropic (Claude)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Model Identifier</label>
                  <input
                    type="text"
                    className="form-input"
                    value={modelInput}
                    onChange={(e) => setModelInput(e.target.value)}
                    placeholder="llama-3.3-70b-versatile"
                  />
                </div>
              </div>

              {baseUrlInput && (
                <div className="form-group">
                  <label>API Base URL</label>
                  <input
                    type="text"
                    className="form-input"
                    value={baseUrlInput}
                    onChange={(e) => setBaseUrlInput(e.target.value)}
                    placeholder="https://api.groq.com/openai/v1"
                  />
                </div>
              )}

              <div className="form-group">
                <label>
                  API Key
                  {llmConfig?.has_api_key && (
                    <span style={{ color: 'var(--success)', marginLeft: '8px', fontSize: '0.8rem' }}>
                      (Active: {llmConfig.masked_key})
                    </span>
                  )}
                </label>
                <input
                  type="password"
                  className="form-input"
                  placeholder={FREE_LLM_PRESETS.find(p => p.id === selectedPreset)?.keyPlaceholder || 'Paste API Key here...'}
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                />
                <small style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '4px', display: 'block' }}>
                  💡 <strong>Tip:</strong> If left empty, the agent runs in <strong>Autonomous Mode</strong> with local tools (Filesystem, Git, Database, and Python) without requiring any paid API keys!
                </small>
              </div>

              <div className="modal-actions" style={{ marginTop: '1.25rem' }}>
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setShowConfigModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-submit"
                  disabled={isSavingConfig}
                >
                  {isSavingConfig ? 'Saving...' : 'Save & Activate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Interactive Command Center / Prompt Console */}
      <section className="command-console">
        <div className="console-header">
          <div className="console-title">
            <span>🎯</span>
            <span>Agent Command Center</span>
          </div>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Direct Neural Execution & Reasoning Loop
          </span>
        </div>

        <div className="prompt-chips">
          {SUGGESTED_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              className="chip"
              onClick={() => {
                setPrompt(p);
                handleExecuteTask(p);
              }}
            >
              ✦ {p}
            </button>
          ))}
        </div>

        <div className="prompt-input-wrapper">
          <textarea
            className="prompt-textarea"
            rows="2"
            placeholder="Instruct the autonomous agent (e.g. 'Synthesize memory and plan strategies for autonomous optimization')..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                handleExecuteTask();
              }
            }}
          />
          <button
            className="btn-execute"
            disabled={isExecuting || !prompt.trim()}
            onClick={() => handleExecuteTask()}
          >
            {isExecuting ? (
              <>
                <span className="pulse-dot" style={{ background: '#fff' }}></span>
                Reasoning...
              </>
            ) : (
              <>
                <span>Execute</span>
                <span>➔</span>
              </>
            )}
          </button>
        </div>

        {/* Live Execution Result Card */}
        {executionResult && (
          <div className="execution-result-card">
            <div className="result-header">
              <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                Task Execution Telemetry: <span style={{ color: 'var(--text-secondary)' }}>{executionResult.task}</span>
              </span>
              <span className={`result-badge ${executionResult.success ? 'success' : 'error'}`}>
                {executionResult.status || (executionResult.success ? 'Completed' : 'Error')}
              </span>
            </div>

            {executionResult.learning && (
              <div className="result-meta-grid">
                <div className="result-meta-box">
                  <div className="result-meta-label">Evaluator Score</div>
                  <div className="result-meta-val" style={{ color: '#10b981' }}>
                    {(executionResult.learning.score * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="result-meta-box">
                  <div className="result-meta-label">Learned Strategy</div>
                  <div className="result-meta-val" style={{ color: '#a78bfa' }}>
                    {executionResult.learning.strategy_used || 'Adaptive planning'}
                  </div>
                </div>
                <div className="result-meta-box">
                  <div className="result-meta-label">Evaluator Feedback</div>
                  <div className="result-meta-val" style={{ fontSize: '0.85rem' }}>
                    {executionResult.learning.feedback || 'Strategy successfully stored.'}
                  </div>
                </div>
              </div>
            )}

            <div className="result-content-box">
              {executionResult.error ? (
                <span style={{ color: '#fb7185' }}>Error: {executionResult.error}</span>
              ) : (
                typeof executionResult.result === 'object'
                  ? JSON.stringify(executionResult.result, null, 2)
                  : String(executionResult.result || 'Task executed successfully.')
              )}
            </div>
          </div>
        )}
      </section>

      {/* Main Grid: Subsystems, Task Queue, Memory Systems, Learning */}
      <main>
        <div className="dashboard-grid">
          <AgentDashboard agentStatus={agentStatus} />
          <TaskQueue tasks={tasks} onAddTask={handleAddTask} />
          <MemoryViewer memoryStats={memoryStats} />
          <LearningProgress learningStats={learningStats} />
        </div>
      </main>
    </div>
  );
}

export default App;