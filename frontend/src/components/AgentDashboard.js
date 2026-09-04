import React from 'react';

const AgentDashboard = ({ agentStatus }) => {
  if (!agentStatus) {
    return (
      <div className="card">
        <h2>Agent Status</h2>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Agent Status</h2>
      <div className="status-grid">
        <div className="status-item">
          <h3>Overall Status</h3>
          <p className={agentStatus.status === 'running' ? 'status-running' : 'status-stopped'}>
            {agentStatus.status}
          </p>
        </div>
        <div className="status-item">
          <h3>Components</h3>
          <ul>
            {Object.entries(agentStatus.components || {}).map(([component, status]) => (
              <li key={component}>
                {component}: <span className={status === 'ok' ? 'status-ok' : 'status-error'}>
                  {status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AgentDashboard;