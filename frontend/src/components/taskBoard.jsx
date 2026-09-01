import React from 'react';
import TaskColumn from './TaskColumn';

const TaskBoard = () => {
  return (
    <div className="task-board">
      <TaskColumn title="Habits" count={5} type="habit" />
      <TaskColumn title="Dailies" count={3} type="daily" />
      <TaskColumn title="To Do's" count={4} type="todo" />
      <TaskColumn title="Rewards" type="reward" />
    </div>
  );
};

export default TaskBoard;