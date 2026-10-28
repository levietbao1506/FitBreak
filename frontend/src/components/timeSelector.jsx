import { useState, Fragment } from 'react';
import "../style/timeSelector.css";

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const hours = Array.from({ length: 15 }, (_, i) => i + 6);

const dayNamesVi = {
  Mon: 'Thứ Hai',
  Tue: 'Thứ Ba',
  Wed: 'Thứ Tư',
  Thu: 'Thứ Năm',
  Fri: 'Thứ Sáu',
  Sat: 'Thứ Bảy',
  Sun: 'Chủ Nhật'
};

const dayTypeLabels = {
  resistance_training: { label: 'Tập Kháng Lực', color: 'badge-resistance' },
  cardio: { label: 'Cardio / LISS', color: 'badge-cardio' },
  hiit: { label: 'HIIT Cường Độ Cao', color: 'badge-hiit' },
  Rest: { label: 'Nghỉ Ngơi', color: 'badge-rest' }
};

const TimeSelector = ({ scheduleData, onScheduleGenerated }) => {
  const [selectedSlots, setSelectedSlots] = useState(new Set());
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [isSelecting, setIsSelecting] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Nếu đã có scheduleData thì mặc định mở chế độ xem thời khóa biểu Notion
  const [isEditing, setIsEditing] = useState(!scheduleData);

  const getSlotKey = (day, hour, isHalf) => `${day}-${hour}-${isHalf ? '30' : '00'}`;

  const handleMouseDown = (key) => {
    setIsMouseDown(true);
    const currentlySelected = selectedSlots.has(key);
    setIsSelecting(!currentlySelected);
    toggleSlot(key, !currentlySelected);
  };

  const handleMouseEnter = (key) => {
    if (isMouseDown) {
      toggleSlot(key, isSelecting);
    }
  };

  const handleMouseUp = () => {
    setIsMouseDown(false);
  };

  const toggleSlot = (key, select) => {
    setSelectedSlots((prev) => {
      const newSet = new Set(prev);
      if (select) {
        newSet.add(key);
      } else {
        newSet.delete(key);
      }
      return newSet;
    });
  };

  const handleGenerateSchedule = async () => {
    setErrorMsg('');
    setLoading(true);

    const token = localStorage.getItem('token');
    if (!token) {
      setErrorMsg('Bạn chưa đăng nhập hoặc phiên làm việc đã hết hạn!');
      setLoading(false);
      return;
    }

    const timetable = {};
    days.forEach((day) => {
      const daySlotsCount = Array.from(selectedSlots).filter((slotKey) =>
        slotKey.startsWith(`${day}-`)
      ).length;

      timetable[day] = [daySlotsCount * 30];
    });

    try {
      const response = await fetch('http://localhost:8000/schedule-maker', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(timetable),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Lỗi khi tạo lịch tập luyện');
      }

      localStorage.setItem('workoutSchedule', JSON.stringify(data));

      if (onScheduleGenerated) {
        onScheduleGenerated(data);
      }
      setIsEditing(false);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectedCount = selectedSlots.size;
  const totalMinutes = selectedCount * 30;
  const totalHours = (totalMinutes / 60).toFixed(1);

  // ==========================================
  // VIEW 1: NOTION-STYLE TIMETABLE
  // ==========================================
  if (scheduleData && !isEditing) {
    let totalWeeklyExercises = 0;
    let totalWeeklyDuration = 0;

    days.forEach(d => {
      const daySlots = scheduleData[d] || [];
      daySlots.forEach(slot => {
        totalWeeklyDuration += slot.total_time || 0;
        totalWeeklyExercises += slot.exercises?.length || 0;
      });
    });

    return (
      <div className="notion-timetable-page">
        {/* NOTION PAGE COVER & HEADER */}
        <div className="notion-header-block">
          <div className="notion-page-icon">🗓️</div>
          <div className="notion-page-title-row">
            <h1 className="notion-page-title">Thời Khóa Biểu Tập Luyện Của Bạn</h1>
            <button 
              className="notion-regenerate-btn"
              onClick={() => setIsEditing(true)}
            >
              <span>⚙️</span> Chọn Lại Giờ & Tạo Lại Lịch
            </button>
          </div>
          <p className="notion-page-desc">
            Kế hoạch phân bổ vận động khoa học trong tuần. Các bài tập sẽ tự động tích hợp vào <b>Tasks</b> hằng ngày của bạn.
          </p>

          <div className="notion-meta-properties">
            <div className="notion-prop">
              <span className="notion-prop-name">👤 Trạng thái</span>
              <span className="notion-prop-tag notion-tag-active">● Active Plan</span>
            </div>
            <div className="notion-prop">
              <span className="notion-prop-name">⏱ Tổng thời lượng</span>
              <span className="notion-prop-val">{totalWeeklyDuration} phút / tuần</span>
            </div>
            <div className="notion-prop">
              <span className="notion-prop-name">🎯 Tổng bài tập</span>
              <span className="notion-prop-val">{totalWeeklyExercises} nhiệm vụ</span>
            </div>
          </div>
        </div>

        {/* NOTION BOARD / TIMETABLE CARDS */}
        <div className="notion-board-grid">
          {days.map((day) => {
            const daySlots = scheduleData[day] || [];
            const hasExercises = daySlots.some(s => s.exercises && s.exercises.length > 0);
            const mainDayType = daySlots[0]?.day_type || 'Rest';
            const badgeMeta = dayTypeLabels[mainDayType] || { label: mainDayType, color: 'badge-rest' };

            return (
              <div key={day} className={`notion-day-column ${!hasExercises ? 'is-rest' : ''}`}>
                <div className="notion-col-header">
                  <div className="notion-day-titles">
                    <span className="notion-day-code">{day}</span>
                    <span className="notion-day-name">{dayNamesVi[day]}</span>
                  </div>
                  <span className={`notion-badge ${badgeMeta.color}`}>
                    {badgeMeta.label}
                  </span>
                </div>

                <div className="notion-col-content">
                  {daySlots.length === 0 || !hasExercises ? (
                    <div className="notion-rest-card">
                      <span className="rest-icon">☕</span>
                      <p className="rest-text">Ngày nghỉ ngơi hồi phục cơ bắp</p>
                    </div>
                  ) : (
                    daySlots.map((slot, sIdx) => (
                      <div key={sIdx} className="notion-slot-group">
                        <div className="notion-slot-meta">
                          <span>⏱ {slot.total_time || 0} phút</span>
                          <span>•</span>
                          <span>{slot.exercises?.length || 0} bài tập</span>
                        </div>

                        <div className="notion-task-list">
                          {slot.exercises?.map((ex, exIdx) => (
                            <div key={exIdx} className="notion-task-card">
                              <div className="notion-task-row">
                                <span className="notion-checkbox-icon">◻</span>
                                <span className="notion-task-name">{ex.exercise || ex.name}</span>
                              </div>
                              <div className="notion-task-details">
                                <span className="notion-pill-mini bodypart">🎯 {ex.body_part || 'Full body'}</span>
                                <span className="notion-pill-mini duration">⏳ {ex.time_need || 5}p</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // ==========================================
  // VIEW 2: TIME SELECTOR GRID
  // ==========================================
  return (
    <div className="time-selector-container" onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}>
      <div className="time-selector-header">
        <div className="time-header-title-group">
          {scheduleData && (
            <button 
              className="notion-back-btn" 
              onClick={() => setIsEditing(false)}
            >
              ← Xem Thời Khóa Biểu Đang Áp Dụng
            </button>
          )}
          <h2>Chọn Thời Gian Rảnh Trong Tuần</h2>
          <p>Kéo hoặc nhấn vào các ô để chọn khung giờ bạn có thể tập luyện (mỗi ô là 30 phút)</p>
        </div>

        <div className="time-header-actions">
          <div className="time-stats-pill">
            <span>Đã chọn:</span>
            <b>{selectedCount} ô ({totalHours} giờ)</b>
          </div>

          <button 
            className="btn-generate-schedule" 
            onClick={handleGenerateSchedule}
            disabled={loading || selectedCount === 0}
          >
            {loading ? 'Đang tạo lịch...' : '✨ Lưu & Tạo Lịch Tập'}
          </button>
        </div>

        {errorMsg && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      <div className="time-grid-wrapper">
        <div className="time-grid">
          <div className="grid-header time-col-header">Giờ</div>
          {days.map((day) => (
            <div key={day} className="grid-header day-col-header">{day}</div>
          ))}

          <div className="time-label-col">
            {hours.map((hour) => (
              <div key={`label-${hour}`} className="time-label">
                {hour}:00
              </div>
            ))}
            <div className="time-label time-label-end">21:00</div>
          </div>

          {days.map((day) => (
            <div key={`col-${day}`} className="day-col">
              {hours.map((hour) => (
                <Fragment key={`slots-${day}-${hour}`}>
                  <div
                    className={`time-slot full-hour ${selectedSlots.has(getSlotKey(day, hour, false)) ? 'selected' : ''}`}
                    onMouseDown={() => handleMouseDown(getSlotKey(day, hour, false))}
                    onMouseEnter={() => handleMouseEnter(getSlotKey(day, hour, false))}
                    title={`${day} ${hour}:00 - ${hour}:30`}
                  ></div>
                  {hour !== 21 && (
                    <div
                      className={`time-slot half-hour ${selectedSlots.has(getSlotKey(day, hour, true)) ? 'selected' : ''}`}
                      onMouseDown={() => handleMouseDown(getSlotKey(day, hour, true))}
                      onMouseEnter={() => handleMouseEnter(getSlotKey(day, hour, true))}
                      title={`${day} ${hour}:30 - ${hour + 1}:00`}
                    ></div>
                  )}
                </Fragment>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TimeSelector;
