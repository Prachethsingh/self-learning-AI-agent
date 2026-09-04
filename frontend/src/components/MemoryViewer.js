import React from 'react';

const MemoryViewer = ({ memoryStats }) => {
  if (!memoryStats) {
    return (
      <div className="card">
        <h2>
          <span>Memory Subsystems</span>
          <span className="icon">💾</span>
        </h2>
        <div className="no-tasks-state">Loading memory architecture...</div>
      </div>
    );
  }

  const shortTerm = memoryStats.short_term_memory || {};
  const longTerm = memoryStats.long_term_memory || {};
  const vector = memoryStats.vector_memory || {};

  return (
    <div className="card">
      <h2>
        <span>Memory Subsystems</span>
        <span className="icon">🧠</span>
      </h2>

      <div className="memory-sections-grid">
        {/* Short-Term Memory Tier */}
        <div className="memory-tier-card">
          <div className="tier-title">
            <span>💾 Short-Term Working Buffer</span>
            <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>RAM Cache</span>
          </div>
          <div className="tier-stat-row">
            <div className="tier-stat-item">
              <div className="num">{shortTerm.active_items || 0}</div>
              <div className="label">Active Context Items</div>
            </div>
            <div className="tier-stat-item">
              <div className="num">{shortTerm.total_items || 0}</div>
              <div className="label">Cumulative Buffer Items</div>
            </div>
          </div>
        </div>

        {/* Long-Term Memory Tier */}
        <div className="memory-tier-card">
          <div className="tier-title">
            <span>🗄️ Long-Term Relational Store</span>
            <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>SQLite / Postgres</span>
          </div>
          <div className="tier-stat-row">
            <div className="tier-stat-item">
              <div className="num">{longTerm.total_items || 0}</div>
              <div className="label">Persisted Records</div>
            </div>
            <div className="tier-stat-item">
              <div className="num">{Object.keys(longTerm.categories || {}).length}</div>
              <div className="label">Memory Categories</div>
            </div>
          </div>
        </div>

        {/* Vector Memory Tier */}
        <div className="memory-tier-card">
          <div className="tier-title">
            <span>🔮 Vector Semantic Space</span>
            <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>all-MiniLM-L6-v2</span>
          </div>
          <div className="tier-stat-row">
            <div className="tier-stat-item">
              <div className="num">{vector.total_points || 0}</div>
              <div className="label">Indexed Embeddings</div>
            </div>
            <div className="tier-stat-item">
              <div className="num" style={{ color: '#10b981', fontSize: '1.1rem', textTransform: 'capitalize' }}>
                {vector.status || 'Active'}
              </div>
              <div className="label">Qdrant Engine</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryViewer;