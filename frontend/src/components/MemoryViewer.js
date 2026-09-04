import React from 'react';

const MemoryViewer = ({ memoryStats }) => {
  if (!memoryStats) {
    return (
      <div className="card">
        <h2>Memory Systems</h2>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Memory Systems</h2>
      <div className="memory-grid">
        <div className="memory-section">
          <h3>Short-Term Memory</h3>
          <div className="memory-stats">
            <div>
              <h4>Active Items</h4>
              <p>{memoryStats.short_term_memory?.active_items || 0}</p>
            </div>
            <div>
              <h4>Total Items</h4>
              <p>{memoryStats.short_term_memory?.total_items || 0}</p>
            </div>
          </div>
        </div>

        <div className="memory-section">
          <h3>Long-Term Memory</h3>
          <div className="memory-stats">
            <div>
              <h4>Total Items</h4>
              <p>{memoryStats.long_term_memory?.total_items || 0}</p>
            </div>
            <div>
              <h4>Categories</h4>
              <p>{Object.keys(memoryStats.long_term_memory?.categories || {}).length}</p>
            </div>
          </div>
        </div>

        <div className="memory-section">
          <h3>Vector Memory</h3>
          <div className="memory-stats">
            <div>
              <h4>Total Points</h4>
              <p>{memoryStats.vector_memory?.total_points || 0}</p>
            </div>
            <div>
              <h4>Status</h4>
              <p>{memoryStats.vector_memory?.status || 'unknown'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryViewer;