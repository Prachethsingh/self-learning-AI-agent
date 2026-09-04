import React, { useState } from 'react';

const TaskQueue = ({ tasks, onAddTask }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(2);
  const [estimatedTime, setEstimatedTime] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const pendingTasks = (tasks || []).filter(task => task.status === 'pending');
  const completedTasks = (tasks || []).filter(task => task.status === 'completed');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    setIsSubmitting(true);
    try {
      if (onAddTask) {
        await onAddTask({
          description: description.trim(),
          priority: Number(priority),
          estimated_time: Number(estimatedTime)
        });
      }
      setDescription('');
      setShowAddForm(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h2>
        <span>Task Queue & Pipeline</span>
        <button
          className="btn-header-action"
          style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ Cancel' : '+ Enqueue Task'}
        </button>
      </h2>

      {showAddForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '18px', background: 'rgba(255,255,255,0.03)', padding: '14px', borderRadius: '12px', border: '1px solid var(--border-accent)' }}>
          <div style={{ marginBottom: '10px' }}>
            <input
              type="text"
              placeholder="Task description (e.g. 'Optimize memory indexing')..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                background: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '0.9rem'
              }}
              required
            />
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Priority:
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                style={{ marginLeft: '6px', background: 'var(--bg-input)', color: '#fff', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '4px 8px' }}
              >
                <option value={1}>1 (High)</option>
                <option value={2}>2 (Medium)</option>
                <option value={3}>3 (Low)</option>
              </select>
            </label>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Est. Hours:
              <input
                type="number"
                min="0.5"
                step="0.5"
                value={estimatedTime}
                onChange={(e) => setEstimatedTime(e.target.value)}
                style={{ marginLeft: '6px', width: '60px', background: 'var(--bg-input)', color: '#fff', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '4px 8px' }}
              />
            </label>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-header-action"
              style={{ marginLeft: 'auto', background: 'var(--accent-purple)', borderColor: 'transparent', color: '#fff' }}
            >
              {isSubmitting ? 'Adding...' : 'Add to Queue'}
            </button>
          </div>
        </form>
      )}

      <div className="task-stats-banner">
        <div className="task-stat-card">
          <div className="lbl">Pending Pipeline</div>
          <div className="val" style={{ color: '#f59e0b' }}>{pendingTasks.length}</div>
        </div>
        <div className="task-stat-card">
          <div className="lbl">Resolved Tasks</div>
          <div className="val" style={{ color: '#10b981' }}>{completedTasks.length}</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {pendingTasks.length > 0 && (
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '8px' }}>
              Pending Execution
            </div>
            <ul className="task-list">
              {pendingTasks.map(task => (
                <li key={task.id} className="task-item pending">
                  <div className="task-content">
                    <h4>{task.description}</h4>
                    <div className="task-meta">
                      <span>Priority: P{task.priority || 1}</span>
                      <span>•</span>
                      <span>Est: {task.estimated_time || 1}h</span>
                    </div>
                  </div>
                  <span className="status-tag ok" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
                    queued
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {completedTasks.length > 0 && (
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '8px' }}>
              Recently Finished
            </div>
            <ul className="task-list">
              {completedTasks.slice(-4).map(task => (
                <li key={task.id} className="task-item completed">
                  <div className="task-content">
                    <h4>{task.description}</h4>
                    <div className="task-meta">
                      <span>Completed: {task.completed_at ? new Date(task.completed_at).toLocaleTimeString() : 'Recently'}</span>
                    </div>
                  </div>
                  <span className="status-tag ok">done</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {pendingTasks.length === 0 && completedTasks.length === 0 && (
          <div className="no-tasks-state">
            <div style={{ fontSize: '1.8rem', marginBottom: '8px' }}>📭</div>
            <div>No active tasks in queue.</div>
            <div style={{ fontSize: '0.8rem', marginTop: '4px', opacity: 0.7 }}>Click "+ Enqueue Task" or execute a prompt above.</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskQueue;