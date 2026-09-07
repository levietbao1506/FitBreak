import React, { useState } from 'react';
import "../style/timeSelector.css"

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
// Các giờ từ 6:00 đến 21:00
const hours = Array.from({ length: 15 }, (_, i) => i + 6);

const TimeSelector = () => {
  const [selectedSlots, setSelectedSlots] = useState(new Set());
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [isSelecting, setIsSelecting] = useState(true);

  // Định dạng key cho mỗi ô: "Day-Hour-Minute"
  const getSlotKey = (day, hour, isHalf) => `${day}-${hour}-${isHalf ? '30' : '00'}`;

  const handleMouseDown = (key) => {
    setIsMouseDown(true);
    const currentlySelected = selectedSlots.has(key);
    setIsSelecting(!currentlySelected); // Nếu ô đã chọn thì chuyển sang chế độ xóa
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

  return (
    <div className="time-selector-container" onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}>
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