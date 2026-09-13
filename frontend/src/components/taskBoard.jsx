import React, { useState, useEffect } from 'react';
import '../style/taskBoard.css';

const daysOfWeekMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const TaskBoard = ({ scheduleData, onUpdateCoins, onUpdateSchedule }) => {
  const [todaySchedule, setTodaySchedule] = useState([]);
  const [todayName, setTodayName] = useState('');
  const [removingTasks, setRemovingTasks] = useState({});

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
      setTodaySchedule(JSON.parse(JSON.stringify(schedule[currentDayKey])));
    } else {
      setTodaySchedule([]);
    }
  }, [scheduleData]);

  const handleTaskComplete = async (slotIndex, exIndex, exerciseItem) => {
    const taskId = `${slotIndex}-${exIndex}`;
    setRemovingTasks((prev) => ({ ...prev, [taskId]: true }));

    const rewardCoins = exerciseItem.reward_coins || 10;
    
    const safeExerciseId = String(exerciseItem.id || exerciseItem.exercise || exerciseItem.name || "0");

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/exercises-log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          exercise_id: safeExerciseId,
          completed_at: new Date().toISOString(),
          reward_coins: rewardCoins
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (onUpdateCoins) {
          onUpdateCoins(data.new_coins);
        }

        setTimeout(() => {
          let fullSchedule = scheduleData ? JSON.parse(JSON.stringify(scheduleData)) : {};
          const currentDayKey = daysOfWeekMap[new Date().getDay()];
          
          if (fullSchedule[currentDayKey] && fullSchedule[currentDayKey][slotIndex]) {
            fullSchedule[currentDayKey][slotIndex].exercises = fullSchedule[currentDayKey][slotIndex].exercises.filter((_, idx) => idx !== exIndex);
          }

          if (onUpdateSchedule) {
            onUpdateSchedule(fullSchedule);
          } else {
            localStorage.setItem('workoutSchedule', JSON.stringify(fullSchedule));
          }
          
          setTodaySchedule(fullSchedule[currentDayKey] || []);
        }, 300);
      } else {
        setRemovingTasks((prev) => ({ ...prev, [taskId]: false }));
        console.error("Lỗi từ server:", await response.text());
      }
    } catch (error) {
      console.error("Lỗi khi gửi dữ liệu hoàn thành:", error);
      setRemovingTasks((prev) => ({ ...prev, [taskId]: false }));
    }
  };

  return (
    <div className="taskboard-container">
      <div className="taskboard-header">
        <h2>Bài tập hôm nay ({todayName})</h2>
      </div>

      {todaySchedule.length === 0 ? (
        <div className="empty-schedule-card">
          <p>Chưa có lịch tập cho hôm nay. Vui lòng vào mục <b>Schedule</b> để tạo lịch!</p>
        </div>
      ) : (
        todaySchedule.map((slot, slotIndex) => {
          const hasExercises = slot.exercises && slot.exercises.length > 0;

          if (slot.day_type === 'Rest') {
            return (
              <div key={slotIndex} className="rest-day-card">
                <h3>Hôm nay là ngày nghỉ (Rest Day)</h3>
                <p>Hãy dành thời gian phục hồi cơ bắp và nghỉ ngơi đầy đủ nhé!</p>
              </div>
            );
          }

          if (!hasExercises) {
            return (
              <div key={slotIndex} className="completed-block">
                <h3>🎉 Bạn đã hoàn thành toàn bộ bài tập trong mục này!</h3>
              </div>
            );
          }

          return (
            <div key={slotIndex} className="workout-block">
              <div className="block-title">
                <h3>Chủ đề: <span className="highlight-type">{(slot.day_type || '').replace('_', ' ').toUpperCase()}</span></h3>
                <span>Thời gian: {slot.total_time} / {slot.slot_budget} phút</span>
              </div>

              <div className="exercise-list">
                {slot.exercises.map((item, exIndex) => {
                  const taskId = `${slotIndex}-${exIndex}`;
                  const isRemoving = !!removingTasks[taskId];

                  const exerciseTitle = item.exercise || item.name || item.exercise_name || "Bài tập";
                  const bodyPart = item.body_part || "Toàn thân";
                  const duration = item.time_need || 0;
                  const level = item["level of physical activity"] || item.level || "Vừa";

                  return (
                    <div key={taskId} className={`exercise-card ${isRemoving ? 'fade-out' : ''}`}>
                      <input
                        type="checkbox"
                        checked={false}
                        onChange={() => handleTaskComplete(slotIndex, exIndex, item)}
                      />
                      <div className="exercise-info">
                        <div className="exercise-header-row">
                          <h4>{exerciseTitle}</h4>
                          <span className="body-part-badge">🎯 {bodyPart}</span>
                        </div>
                        <p>⏱ Thời lượng: <b>{duration} phút</b> | Cấp độ: <span className="level-text">{level}</span></p>
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