import React, { useState, useEffect } from 'react';
import useWebSocket from './hooks/useWebSocket';
import AgentDashboard from './components/AgentDashboard';
import TaskQueue from './components/TaskQueue';
import MemoryViewer from './components/MemoryViewer';
import LearningProgress from './components/LearningProgress';
import './App.css';

function App() {
  const [agentStatus, setAgentStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [memoryStats, setMemoryStats] = useState(null);
  const [learningStats, setLearningStats] = useState(null);

  // WebSocket connection for real-time updates
  const { data: wsData, isConnected: wsConnected } = useWebSocket('ws://localhost:8000/ws');

  useEffect(() => {
    // Fetch initial data
    fetchAgentStatus();
    fetchTasks();
    fetchMemoryStats();
    fetchLearningStats();

    // Handle WebSocket updates
    if (wsData) {
      handleWebSocketUpdate(wsData);
    }

    // Set up interval for fallback updates (in case WebSocket fails)
    const interval = setInterval(() => {
      fetchAgentStatus();
      fetchTasks();
      fetchMemoryStats();
      fetchLearningStats();
    }, 10000); // Update every 10 seconds as backup

    return () => clearInterval(interval);
  }, [wsData]);

  const handleWebSocketUpdate = (data) => {
    switch (data.type) {
      case 'agent_update':
        setAgentStatus(prev => ({ ...prev, ...data.data }));
        break;
      case 'task_update':
        setTasks(prev => {
          // Update or add task
          const updatedTasks = prev.map(task =>
            task.id === data.data.id ? data.data : task
          );
          // If task doesn't exist, add it
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
      const data = await response.json();
      setAgentStatus(data);
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/tasks/');
      const data = await response.json();
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchMemoryStats = async () => {
    try {
      const response = await fetch('/api/memory/stats');
      const data = await response.json();
      setMemoryStats(data);
    } catch (error) {
      console.error('Error fetching memory stats:', error);
    }
  };

  const fetchLearningStats = async () => {
    try {
      const response = await fetch('/api/agent/status');
      const data = await response.json();
      setLearningStats(data.stats?.learning || {});
    } catch (error) {
      console.error('Error fetching learning stats:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Self-Learning AI Agent Dashboard</h1>
        <p>Monitoring and controlling your AI agent's learning process</p>
        {wsConnected && <span className="ws-status">● Connected</span>}
        {!wsConnected && <span className="ws-status">● Disconnected (using polling)</span>}
      </header>
      <main>
        <div className="dashboard-grid">
          <AgentDashboard agentStatus={agentStatus} />
          <TaskQueue tasks={tasks} />
          <MemoryViewer memoryStats={memoryStats} />
          <LearningProgress learningStats={learningStats} />
        </div>
      </main>
    </div>
  );
}

export default App;