import React from 'react';

const LearningProgress = ({ learningStats }) => {
  if (!learningStats) {
    return (
      <div className="card">
        <h2>
          <span>Learning & Evolution Metrics</span>
          <span className="icon">📈</span>
        </h2>
        <div className="no-tasks-state">Evaluating agent experience repository...</div>
      </div>
    );
  }

  const successRate = (learningStats.success_rate || 0) * 100;
  const totalExp = learningStats.total_experiences || 0;
  const successfulExp = learningStats.successful_experiences || 0;
  const uniqueTasks = learningStats.unique_tasks || 0;
  const strategies = learningStats.strategies_learned || 0;

  return (
    <div className="card">
      <h2>
        <span>Self-Learning & Evolution</span>
        <span className="icon">🚀</span>
      </h2>

      <div className="learning-stats-grid">
        <div className="stat-box-modern">
          <div className="metric" style={{ color: '#06b6d4' }}>{totalExp}</div>
          <div className="caption">Total Experiences</div>
        </div>
        <div className="stat-box-modern">
          <div className="metric" style={{ color: '#10b981' }}>{successfulExp}</div>
          <div className="caption">Successful Cycles</div>
        </div>
        <div className="stat-box-modern">
          <div className="metric" style={{ color: '#a78bfa' }}>{successRate.toFixed(0)}%</div>
          <div className="caption">Success Rate</div>
        </div>
        <div className="stat-box-modern">
          <div className="metric" style={{ color: '#f59e0b' }}>{strategies}</div>
          <div className="caption">Strategies Acquired</div>
        </div>
      </div>

      <div className="learning-insight-banner">
        <div style={{ fontWeight: 700, color: '#fff', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>💡</span>
          <span>Continuous Self-Improvement Engine</span>
        </div>
        After every task execution, the Evaluator computes a performance score and the Learner stores verified heuristic strategies into memory to refine subsequent planning.
      </div>
    </div>
  );
};

export default LearningProgress;