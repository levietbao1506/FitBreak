import React, { useState, useEffect } from 'react';
import '../style/taskBoard.css';

const daysOfWeekMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const TaskBoard = ({ scheduleData }) => {
  const [todaySchedule, setTodaySchedule] = useState([]);
  const [todayName, setTodayName] = useState('');
  const [completedTasks, setCompletedTasks] = useState({});

  useEffect(() => {
    const currentDayIndex = new Date().getDay();
    const currentDayKey = daysOfWeekMap[currentDayIndex];
    setTodayName(currentDayKey);

    let schedule = scheduleData;
    if (!schedule) {
      const savedSchedule = localStorage.getItem('workoutSchedule');
      if (savedSchedule) {
        try {
          schedule = JSON.parse(savedSchedule);
        } catch (e) {
          console.error("Lỗi parse lịch tập:", e);
        }
      }
    }

    if (schedule && schedule[currentDayKey]) {
      setTodaySchedule(schedule[currentDayKey]);
    } else {
      setTodaySchedule([]);
    }
  }, [scheduleData]);

  const toggleTaskComplete = (index) => {
    setCompletedTasks((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="taskboard-container">
      <div className="taskboard-header">
        <h2>Bài tập hôm nay ({todayName})</h2>
      </div>

      {todaySchedule.length === 0 ? (
        <div className="empty-schedule-card">
          <p>Chưa có lịch tập cho hôm nay. Vui lòng vào mục <b>Schedule</b> để đăng ký thời gian rảnh và tạo lịch!</p>
        </div>
      ) : (
        todaySchedule.map((slot, slotIndex) => {
          if (slot.day_type === 'Rest' || !slot.exercises || slot.exercises.length === 0) {
            return (
              <div key={slotIndex} className="rest-day-card">
                <h3> Hôm nay là ngày nghỉ (Rest Day)</h3>
                <p>Hãy dành thời gian phục hồi cơ bắp và nghỉ ngơi đầy đủ nhé!</p>
              </div>
            );
          }

          return (
            <div key={slotIndex} className="workout-block">
              <div className="block-title">
                <h3>Chủ đề: <span className="highlight-type">{slot.day_type.replace('_', ' ').toUpperCase()}</span></h3>
                <span>Thời gian: {slot.total_time} / {slot.slot_budget} phút</span>
              </div>

              <div className="exercise-list">
                {slot.exercises.map((exercise, exIndex) => {
                  const taskId = `${slotIndex}-${exIndex}`;
                  const isDone = !!completedTasks[taskId];

                  return (
                    <div key={taskId} className={`exercise-card ${isDone ? 'completed' : ''}`}>
                      <input
                        type="checkbox"
                        checked={isDone}
                        onChange={() => toggleTaskComplete(taskId)}
                      />
                      <div className="exercise-info">
                        <h4>{exercise.name || exercise["exercise_name"] || "Bài tập"}</h4>
                        <p>⏱ Thời lượng: <b>{exercise.time_need} phút</b> | Cấp độ: {exercise["level of physical activity"] || "Vừa"}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default TaskBoard;