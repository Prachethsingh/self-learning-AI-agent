import React from 'react';

const LearningProgress = ({ learningStats }) => {
  if (!learningStats) {
    return (
      <div className="card">
        <h2>Learning Progress</h2>
        <p>Loading...</p>
      </div>
    );
  }

  const successRate = (learningStats.success_rate || 0) * 100;

  return (
    <div className="card">
      <h2>Learning Progress</h2>
      <div className="learning-grid">
        <div className="learning-stat">
          <h3>Total Experiences</h3>
          <p>{learningStats.total_experiences || 0}</p>
        </div>
        <div className="learning-stat">
          <h3>Successful Experiences</h3>
          <p>{learningStats.successful_experiences || 0}</p>
        </div>
        <div className="learning-stat">
          <h3>Success Rate</h3>
          <p>{successRate.toFixed(1)}%</p>
        </div>
        <div className="learning-stat">
          <h3>Unique Tasks</h3>
          <p>{learningStats.unique_tasks || 0}</p>
        </div>
        <div className="learning-stat">
          <h3>Strategies Learned</h3>
          <p>{learningStats.strategies_learned || 0}</p>
        </div>
      </div>

      <div className="learning-note">
        <p>The agent learns from each task execution, storing experiences and improving its strategies over time.</p>
      </div>
    </div>
  );
};

export default LearningProgress;