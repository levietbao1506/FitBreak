import React from 'react';

const TaskCard = ({ title, type }) => {
  return (
    <div className={`task-card ${type}`}>
      {type === 'habit' && (
        <div className="habit-controls">
          <button className="btn-plus">+</button>
        </div>
      )}
      
      {(type === 'daily' || type === 'todo') && (
        <div className="checkbox"></div>
      )}

      <div className="task-content">
        <p>{title}</p>
        <span className="sub-text">Tap to edit...</span>
      </div>

      {type === 'habit' && (
        <div className="habit-controls">
          <button className="btn-minus">-</button>
        </div>
      )}
      
      {type === 'reward' && (
        <div className="reward-cost">🪙 10</div>
      )}
    </div>
  );
};

export default TaskCard;