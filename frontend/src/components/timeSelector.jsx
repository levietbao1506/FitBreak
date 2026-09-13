// src/components/TimeSelector.jsx
import React, { useState } from 'react';
import "../style/timeSelector.css";

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const hours = Array.from({ length: 15 }, (_, i) => i + 6);

const TimeSelector = ({ onScheduleGenerated }) => {
  const [selectedSlots, setSelectedSlots] = useState(new Set());
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [isSelecting, setIsSelecting] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

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
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="time-selector-container" onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}>
      <div className="time-selector-header">
        <h2>Chọn thời gian rảnh trong tuần</h2>
        
        <button 
          className="btn-generate-schedule" 
          onClick={handleGenerateSchedule}
          disabled={loading}
        >
          {loading ? 'Đang tạo lịch...' : 'Lưu & Tạo Lịch Tập'}
        </button>

        {errorMsg && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      <div className="time-grid">
        <div className="grid-header">Time</div>
        {days.map((day) => (
          <div key={day} className="grid-header">{day}</div>
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
              <React.Fragment key={`slots-${day}-${hour}`}>
                <div
                  className={`time-slot full-hour ${selectedSlots.has(getSlotKey(day, hour, false)) ? 'selected' : ''}`}
                  onMouseDown={() => handleMouseDown(getSlotKey(day, hour, false))}
                  onMouseEnter={() => handleMouseEnter(getSlotKey(day, hour, false))}
                ></div>
                {hour !== 21 && (
                  <div
                    className={`time-slot half-hour ${selectedSlots.has(getSlotKey(day, hour, true)) ? 'selected' : ''}`}
                    onMouseDown={() => handleMouseDown(getSlotKey(day, hour, true))}
                    onMouseEnter={() => handleMouseEnter(getSlotKey(day, hour, true))}
                  ></div>
                )}
              </React.Fragment>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TimeSelector;