import React, { useState, useEffect } from 'react';
import '../style/taskBoard.css';

const daysOfWeekMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Danh sách các bài tập nhẹ ngẫu nhiên sau mỗi 25 phút
const MINI_TASKS = [
  "Hít đất 10 cái",
  "Đi uống 1 cốc nước đầy",
  "Vươn vai và nhắm mắt thư giãn 2 phút",
  "Squat 15 cái",
  "Đi bộ quanh phòng 2 phút",
  "Giãn cơ vai và lưng 5 phút"
];

const TaskBoard = ({ scheduleData, onUpdateCoins, onUpdateSchedule }) => {
  // --- State của Lịch tập chính ---
  const [todaySchedule, setTodaySchedule] = useState([]);
  const [todayName, setTodayName] = useState('');
  const [removingTasks, setRemovingTasks] = useState({});

  // --- State của Đồng hồ Pomodoro ---
  const POMODORO_TIME = 25*60;
  // const POMODORO_TIME = 25 * 60; // 25 phút tính bằng giây
  const [timeLeft, setTimeLeft] = useState(POMODORO_TIME);
  const [isRunning, setIsRunning] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const [currentMiniTask, setCurrentMiniTask] = useState("");
  const [isCompletingMini, setIsCompletingMini] = useState(false);

  // Yêu cầu quyền hiển thị thông báo trình duyệt khi lần đầu load trang
  useEffect(() => {
    if ("Notification" in window && Notification.permission !== "granted") {
      Notification.requestPermission();
    }
  }, []);

  // Khởi tạo lịch tập
  useEffect(() => {
    const currentDayKey = daysOfWeekMap[new Date().getDay()];
    setTodayName(currentDayKey);

    if (scheduleData && scheduleData[currentDayKey]) {
      setTodaySchedule(JSON.parse(JSON.stringify(scheduleData[currentDayKey])));
    } else {
      setTodaySchedule([]);
    }
  }, [scheduleData]);

  // Logic Đồng hồ đếm ngược
  useEffect(() => {
    let interval = null;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (isRunning && timeLeft === 0) {
      // Khi hết giờ
      setIsRunning(false);
      setIsBreak(true);
      
      // Chọn ngẫu nhiên 1 bài tập nhẹ
      const randomTask = MINI_TASKS[Math.floor(Math.random() * MINI_TASKS.length)];
      setCurrentMiniTask(randomTask);
      
      // Gửi thông báo qua Web Notification
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("Hết 25 phút rồi! 🔥", {
          body: `Tới lúc nghỉ ngơi. Hãy đứng lên và: ${randomTask}`,
          icon: "/favicon.ico" // Thay bằng icon trang web của bạn nếu có
        });
      }
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  // Hàm định dạng thời gian Pomodoro hiển thị
  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  // Hàm xử lý khi hoàn thành bài tập nhẹ (nhận 2 coins)
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


        console.log('%c[TaskBoard] Chuẩn bị dispatch raid:boss-updated với data.boss =', 'color: cyan; font-weight: bold;', data.boss);
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

  // Hàm xử lý hoàn thành bài tập chính
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
      {/* CỘT TRÁI (hoặc Phải tuỳ CSS): Đồng hồ Pomodoro */}
      <div className="pomodoro-sidebar">
        <h3>🔥 Pomodoro Thể Chất</h3>
        {!isBreak ? (
          <div className="timer-section">
            <div className="timer-display">{formatTime(timeLeft)}</div>
            <p className="timer-desc">Tập trung làm việc. Nghỉ ngơi vận động sau mỗi 25 phút!</p>
            <div className="timer-controls">
              <button 
                className={`btn-timer ${isRunning ? 'btn-pause' : 'btn-start'}`}
                onClick={() => {
                  // 1. Xin quyền gửi thông báo ngay khi người dùng tương tác click
                  if ("Notification" in window && Notification.permission !== "granted") {
                    Notification.requestPermission().then(permission => {
                      if (permission === "granted") {
                        console.log("Đã được cấp quyền thông báo!");
                      }
                    });
                  }
                  setIsRunning(!isRunning);
                }}
              >
                {isRunning ? 'Tạm dừng' : 'Bắt đầu'}
              </button>
              <button 
                className="btn-timer btn-reset"
                onClick={() => {
                  setIsRunning(false);
                  setTimeLeft(POMODORO_TIME);
                }}
              >
                Reset
              </button>
            </div>
          </div>
        ) : (
          <div className="break-section fade-in">
            <div className="break-icon">⏰</div>
            <h4 className="break-title">Đã hết 25 phút!</h4>
            <p className="break-task-text">Đứng lên và thực hiện:</p>
            <div className="highlight-task">{currentMiniTask}</div>
            <button 
              className="btn-complete-mini"
              disabled={isCompletingMini}
              onClick={handleMiniTaskComplete}
            >
              {isCompletingMini ? 'Đang gửi...' : 'Hoàn thành (+2 Coins)'}
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

      {/* CỘT CHÍNH: Lịch tập */}
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
    </div>
  );
};

export default TaskBoard;