import React, { useState, useEffect } from 'react';
import useWebSocket from './hooks/useWebSocket';
import AgentDashboard from './components/AgentDashboard';
import TaskQueue from './components/TaskQueue';
import MemoryViewer from './components/MemoryViewer';
import LearningProgress from './components/LearningProgress';
import './App.css';

const SUGGESTED_PROMPTS = [
  "Analyze current memory state and summarize active subsystems",
  "Research autonomous agent architectures using web search",
  "Plan and decompose a multi-step data processing workflow",
  "Execute a Python benchmark for matrix multiplication algorithms"
];

function App() {
  const [agentStatus, setAgentStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [memoryStats, setMemoryStats] = useState(null);
  const [learningStats, setLearningStats] = useState(null);
  
  // Interactive Agent Console state
  const [prompt, setPrompt] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'console' | 'tasks' | 'memory'

  // WebSocket connection for real-time updates
  const { data: wsData, isConnected: wsConnected } = useWebSocket('ws://localhost:8000/ws');

  const fetchAllData = async () => {
    fetchAgentStatus();
    fetchTasks();
    fetchMemoryStats();
    fetchLearningStats();
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
      const response = await fetch('/api/agent/status');
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
      const response = await fetch('/api/tasks/');
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
      const response = await fetch('/api/memory/stats');
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
      const response = await fetch('/api/agent/status');
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
      const response = await fetch('/api/agent/execute', {
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
    const response = await fetch('/api/tasks/', {
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
      await fetch('/api/agent/reset', { method: 'POST' });
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