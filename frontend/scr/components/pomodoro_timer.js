const WORK_TIME = 25 * 60; // 25 phút
const BREAK_TIME = 5 * 60;  // 5 phút

let currentMode = "IDLE";
let timeLeft = WORK_TIME;
let timerInterval = null;

async function requestNotification() {
  if ("Notification" in window && Notification.permission !== "granted") {
    await Notification.requestPermission();
  }
}

function sendNotification(title, message) {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, {
      body: message,
      icon: "https://cdn-icons-png.flaticon.com/512/2964/2964514.png"
    });
  }
}

function updateDisplay() {
  const minutes = Math.floor(timeLeft / 60).toString().padStart(2, '0');
  const seconds = (timeLeft % 60).toString().padStart(2, '0');
  document.getElementById("timer-display").textContent = `${minutes}:${seconds}`;
  
  const label = currentMode === "WORK" ? "Đang làm việc (Tập trung)" : 
                currentMode === "BREAK" ? "Nghỉ ngơi - Đi bộ / Vận động nhẹ" : "Đã dừng";
  document.getElementById("status-label").textContent = label;
  document.title = `(${minutes}:${seconds}) ${label}`;
}

function switchCycle() {
  if (currentMode === "WORK") {
    currentMode = "BREAK";
    timeLeft = BREAK_TIME;
    sendNotification("Hết giờ làm việc! 🚶‍♂️", "Hãy đứng dậy đi bộ, làm cardio nhẹ trong 5 phút nhé.");
  } else if (currentMode === "BREAK") {
    currentMode = "WORK";
    timeLeft = WORK_TIME;
    sendNotification("Hết giờ nghỉ ngơi! 💻", "Quay trở lại làm việc tập trung nào.");
  }
  updateDisplay();
}

function startShift() {
  requestNotification();
  currentMode = "WORK";
  timeLeft = WORK_TIME;
  
  document.getElementById("btn-start").disabled = true;
  document.getElementById("btn-stop").disabled = false;
  updateDisplay();

  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timeLeft--;
    if (timeLeft < 0) {
      switchCycle();
    } else {
      updateDisplay();
    }
  }, 1000);
}

function stopShift() {
  clearInterval(timerInterval);
  currentMode = "IDLE";
  timeLeft = WORK_TIME;
  
  document.getElementById("btn-start").disabled = false;
  document.getElementById("btn-stop").disabled = true;
  document.getElementById("status-label").textContent = "Ca làm việc đã kết thúc";
  document.getElementById("timer-display").textContent = "25:00";
  document.title = "Pomodoro";
}