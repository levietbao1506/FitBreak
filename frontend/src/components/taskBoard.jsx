import { useState, useEffect } from 'react';
import '../style/taskBoard.css';

const daysOfWeekMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const MINI_TASKS = [
  "Hít đất 10 cái",
  "Đi uống 1 cốc nước đầy",
  "Vươn vai và nhắm mắt thư giãn 2 phút",
  "Squat 15 cái",
  "Đi bộ quanh phòng 2 phút",
  "Giãn cơ vai và lưng 5 phút"
];

const TaskBoard = ({ scheduleData, onUpdateCoins, onUpdateSchedule }) => {
  const [todaySchedule, setTodaySchedule] = useState([]);
  const [todayName, setTodayName] = useState('');
  const [removingTasks, setRemovingTasks] = useState({});

  const POMODORO_TIME = 25 * 60;
  const [timeLeft, setTimeLeft] = useState(POMODORO_TIME);
  const [isRunning, setIsRunning] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const [currentMiniTask, setCurrentMiniTask] = useState("");
  const [isCompletingMini, setIsCompletingMini] = useState(false);

  useEffect(() => {
    if ("Notification" in window && Notification.permission !== "granted") {
      Notification.requestPermission();
    }
  }, []);

  useEffect(() => {
    const currentDayKey = daysOfWeekMap[new Date().getDay()];
    setTodayName(currentDayKey);

    if (scheduleData && scheduleData[currentDayKey]) {
      setTodaySchedule(JSON.parse(JSON.stringify(scheduleData[currentDayKey])));
    } else {
      setTodaySchedule([]);
    }
  }, [scheduleData]);

  useEffect(() => {
    let interval = null;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (isRunning && timeLeft === 0) {
      setIsRunning(false);
      setIsBreak(true);
      
      const randomTask = MINI_TASKS[Math.floor(Math.random() * MINI_TASKS.length)];
      setCurrentMiniTask(randomTask);
      
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("Hết 25 phút rồi! 🔥", {
          body: `Tới lúc nghỉ ngơi. Hãy đứng lên và: ${randomTask}`,
          icon: "/favicon.ico"
        });
      }
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const handleMiniTaskComplete = async () => {
    setIsCompletingMini(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/exercises-log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          exercise_id: "mini_break_task",
          completed_at: new Date().toISOString(),
          reward_coins: 2
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (onUpdateCoins) {
          onUpdateCoins(data.new_coins);
        }
        setIsBreak(false);
        setTimeLeft(POMODORO_TIME);

        window.dispatchEvent(new CustomEvent('raid:boss-updated', { detail: data.boss }));
      } else {
        console.error("Lỗi server khi hoàn thành mini task");
      }
    } catch (error) {
      console.error("Lỗi kết nối:", error);
    } finally {
      setIsCompletingMini(false);
    }
  };

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
        if (onUpdateCoins) onUpdateCoins(data.new_coins);

        setTimeout(() => {
          let fullSchedule = scheduleData ? JSON.parse(JSON.stringify(scheduleData)) : {};
          const currentDayKey = daysOfWeekMap[new Date().getDay()];
          
          if (fullSchedule[currentDayKey] && fullSchedule[currentDayKey][slotIndex]) {
            fullSchedule[currentDayKey][slotIndex].exercises = fullSchedule[currentDayKey][slotIndex].exercises.filter((_, idx) => idx !== exIndex);
          }

          if (onUpdateSchedule) {
            onUpdateSchedule(fullSchedule);
          }
          
          setTodaySchedule(fullSchedule[currentDayKey] || []);

          window.dispatchEvent(new CustomEvent('raid:boss-updated', { detail: data.boss }));
        }, 300);
      } else {
        setRemovingTasks((prev) => ({ ...prev, [taskId]: false }));
      }
    } catch (error) {
      console.error("Lỗi khi gửi dữ liệu hoàn thành:", error);
      setRemovingTasks((prev) => ({ ...prev, [taskId]: false }));
    }
  };

  return (
    <div className="taskboard-page-wrapper">
      <div className="pomodoro-sidebar">
        <div className="pomodoro-header-row">
          <span className="pomodoro-badge">FITNESS FOCUS</span>
          <h3>🔥 Pomodoro Thể Chất</h3>
        </div>

        {!isBreak ? (
          <div className="timer-section">
            <div className="timer-display-wrapper">
              <div className={`timer-display ${isRunning ? 'timer-running' : ''}`}>
                {formatTime(timeLeft)}
              </div>
              <div className="timer-mode-tag">
                {isRunning ? '🟢 Active Focus' : '⚪ Paused'}
              </div>
            </div>

            <p className="timer-desc">Tập trung làm việc. Nghỉ ngơi vận động sau mỗi 25 phút!</p>

            <div className="timer-controls">
              <button 
                className={`btn-timer ${isRunning ? 'btn-pause' : 'btn-start'}`}
                onClick={() => {
                  if ("Notification" in window && Notification.permission !== "granted") {
                    Notification.requestPermission();
                  }
                  setIsRunning(!isRunning);
                }}
              >
                {isRunning ? '⏸ Tạm dừng' : '▶ Bắt đầu'}
              </button>
              <button 
                className="btn-timer btn-reset"
                onClick={() => {
                  setIsRunning(false);
                  setTimeLeft(POMODORO_TIME);
                }}
              >
                ↺ Reset
              </button>
            </div>
          </div>
        ) : (
          <div className="break-section fade-in">
            <div className="break-badge-alert">BREAK TIME</div>
            <div className="break-icon">⏰</div>
            <h4 className="break-title">Đã hết 25 phút!</h4>
            <p className="break-task-text">Đứng lên và thực hiện:</p>
            <div className="highlight-task">{currentMiniTask}</div>
            <button 
              className="btn-complete-mini"
              disabled={isCompletingMini}
              onClick={handleMiniTaskComplete}
            >
              {isCompletingMini ? 'Đang gửi...' : '✓ Hoàn thành (+2 Coins)'}
            </button>
            <button 
              className="btn-skip-mini"
              onClick={() => {
                setIsBreak(false);
                setTimeLeft(POMODORO_TIME);
              }}
            >
              Bỏ qua lần này
            </button>
          </div>
        )}
      </div>

      <div className="taskboard-container">
        <div className="taskboard-header">
          <div className="taskboard-header-content">
            <h2>Bài tập hôm nay</h2>
            <span className="taskboard-day-chip">{todayName}</span>
          </div>
        </div>

        {todaySchedule.length === 0 ? (
          <div className="empty-schedule-card">
            <div className="empty-icon">📅</div>
            <h3>Chưa có lịch tập cho hôm nay</h3>
            <p>Vui lòng vào mục <b>Schedule</b> để chọn khung giờ và tạo lịch tập mới!</p>
          </div>
        ) : (
          todaySchedule.map((slot, slotIndex) => {
            const hasExercises = slot.exercises && slot.exercises.length > 0;

            if (slot.day_type === 'Rest') {
              return (
                <div key={slotIndex} className="rest-day-card">
                  <div className="rest-day-icon">🌿</div>
                  <h3>Hôm nay là ngày nghỉ (Rest Day)</h3>
                  <p>Hãy dành thời gian phục hồi cơ bắp và nghỉ ngơi đầy đủ nhé!</p>
                </div>
              );
            }

            if (!hasExercises) {
              return (
                <div key={slotIndex} className="completed-block">
                  <div className="completed-icon">🎉</div>
                  <h3>Bạn đã hoàn thành toàn bộ bài tập trong mục này!</h3>
                  <p>Tuyệt vời! Tiếp tục giữ vững phong độ nhé.</p>
                </div>
              );
            }

            return (
              <div key={slotIndex} className="workout-block">
                <div className="block-title">
                  <div className="block-title-main">
                    <span className="block-title-icon">⚔️</span>
                    <h3>Chủ đề: <span className="highlight-type">{(slot.day_type || '').replace('_', ' ').toUpperCase()}</span></h3>
                  </div>
                  <span className="block-time-badge">⏱ {slot.total_time} / {slot.slot_budget} phút</span>
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
                        <div className="exercise-checkbox-wrapper">
                          <input
                            type="checkbox"
                            id={`chk-${taskId}`}
                            className="exercise-checkbox"
                            checked={false}
                            onChange={() => handleTaskComplete(slotIndex, exIndex, item)}
                          />
                        </div>
                        <div className="exercise-info">
                          <div className="exercise-header-row">
                            <h4>{exerciseTitle}</h4>
                            <span className="body-part-badge">🎯 {bodyPart}</span>
                          </div>
                          <div className="exercise-meta-row">
                            <span className="exercise-duration">⏱ <b>{duration} phút</b></span>
                            <span className="exercise-meta-separator">•</span>
                            <span className="exercise-level">Cấp độ: <span className="level-text">{level}</span></span>
                            <span className="exercise-meta-separator">•</span>
                            <span className="exercise-reward-tag">+{item.reward_coins || 10} Coins</span>
                          </div>
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
    </div>
  );
};

export default TaskBoard;