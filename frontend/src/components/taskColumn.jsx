import React from 'react';
import TaskCard from './TaskCard';

const TaskColumn = ({ title, count, type }) => {
  return (
    <div className="task-column">
      <div className="column-header">
        <h2>{title} {count !== undefined && <span className="badge">{count}</span>}</h2>
        <div className="filters">
          <span>All</span>
          <span>Active</span>
        </div>
      </div>
      
      <div className="add-task-input">
        <input type="text" placeholder={`Add a ${title}...`} />
      </div>

      <div className="task-list">
        {/* Render mẫu một vài thẻ */}
        <TaskCard title="Sample Task 1" type={type} />
        <TaskCard title="Sample Task 2" type={type} />
        <TaskCard title="Sample Task 3" type={type} />
      </div>
    </div>
  );
};

export default TaskColumn;