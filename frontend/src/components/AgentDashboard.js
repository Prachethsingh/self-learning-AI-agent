import React from 'react';

const componentIcons = {
  brain: '🧠',
  planner: '📋',
  executor: '⚡',
  evaluator: '⚖️',
  learner: '📈',
  short_term_memory: '💾',
  long_term_memory: '🗄️',
  vector_memory: '🔮'
};

const AgentDashboard = ({ agentStatus }) => {
  if (!agentStatus) {
    return (
      <div className="card">
        <h2>
          <span>Agent Core Status</span>
          <span className="icon">⚡</span>
        </h2>
        <div className="no-tasks-state">Loading agent subsystems...</div>
      </div>
    );
  }

  const isRunning = agentStatus.status === 'running';

  return (
    <div className="card">
      <h2>
        <span>Agent Core Subsystems</span>
        <span className="icon">🤖</span>
      </h2>

      <div className="status-grid">
        <div className="overall-status-banner">
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Autonomous Loop Status
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: '2px' }}>
              {isRunning ? 'Active & Ready' : 'Paused / Idle'}
            </div>
          </div>
          <div className={`status-badge-lg ${isRunning ? 'running' : 'stopped'}`}>
            <span className="pulse-dot"></span>
            {agentStatus.status || 'unknown'}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '10px' }}>
            Active Architecture Nodes
          </div>
          <div className="components-grid">
            {Object.entries(agentStatus.components || {}).map(([component, status]) => {
              const icon = componentIcons[component] || '⚙️';
              const cleanName = component.replace(/_/g, ' ');
              const isOk = status === 'ok' || status === 'green';

              return (
                <div key={component} className="component-pill">
                  <div className="component-pill-name">
                    <span>{icon}</span>
                    <span>{cleanName}</span>
                  </div>
                  <span className={`status-tag ${isOk ? 'ok' : 'error'}`}>
                    {status}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentDashboard;