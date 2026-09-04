import React from 'react';

const TaskQueue = ({ tasks }) => {
  if (!tasks) {
    return (
      <div className="card">
        <h2>Task Queue</h2>
        <p>Loading...</p>
      </div>
    );
  }

  const pendingTasks = tasks.filter(task => task.status === 'pending');
  const completedTasks = tasks.filter(task => task.status === 'completed');

  return (
    <div className="card">
      <h2>Task Queue</h2>
      <div className="task-stats">
        <div>
          <h3>Pending Tasks: {pendingTasks.length}</h3>
        </div>
        <div>
          <h3>Completed Tasks: {completedTasks.length}</h3>
        </div>
      </div>

      {pendingTasks.length > 0 && (
        <div className="task-section">
          <h3>Pending Tasks</h3>
          <ul className="task-list">
            {pendingTasks.map(task => (
              <li key={task.id} className="task-item">
                <div className="task-content">
                  <h4>{task.description}</h4>
                  <p className="task-meta">
                    Priority: {task.priority} |
                    Estimated: {task.estimated_time}h
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {completedTasks.length > 0 && (
        <div className="task-section">
          <h3>Recently Completed</h3>
          <ul className="task-list">
            {completedTasks.slice(-5).map(task => (
              <li key={task.id} className="task-item completed">
                <div className="task-content">
                  <h4>{task.description}</h4>
                  <p className="task-meta">
                    Completed: {new Date(task.completed_at).toLocaleTimeString()}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {pendingTasks.length === 0 && completedTasks.length === 0 && (
        <p className="no-tasks">No tasks in queue</p>
      )}
    </div>
  );
};

export default TaskQueue;