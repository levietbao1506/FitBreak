# 🍽️ Food Suggestion Feature - Development Log

## 2026-09-01 22:25 - Khởi tạo dự án
- **Trạng thái**: Bắt đầu phát triển
- **Nhiệm vụ**: Xây dựng tính năng gợi ý thực đơn ăn uống cá nhân hóa
- **Yêu cầu chính**:
  - Quiz khảo sát: Budget, Mục tiêu, Chế độ ăn, Dị ứng
  - Hiển thị kết quả 3 bữa/ngày (Sáng, Trưa, Tối)
  - UI Minimalism, responsive, CSS prefix food-
  - Mock data mẫu cho các gợi ý

### Phân tích cấu trúc hiện tại
- Dự án FitBreak đã có Pomodoro Timer (index.html, pomodoro_timer.js)
- Sẽ tạo file riêng: food_suggestion.html (all-in-one)
- Giữ phong cách thiết kế nhất quán với dark theme hiện tại

### Kế hoạch triển khai
1. [x] Khảo sát cấu trúc dự án
2. [x] Tạo log file
3. [ ] Viết HTML/CSS/JS cho food_suggestion.html
4. [ ] Kiểm tra và hoàn thiện

## 2026-09-01 22:29 - Hoàn thành viết code
- **Trạng thái**: Đã tạo file food_suggestion.html (all-in-one)
- **Chi tiết file**: ~800 dòng code bao gồm:
  - HTML: Quiz form (Budget, Goal, Diet, Allergies) + Result view (Summary, Stats, Meal Cards)
  - CSS: ~380 dòng, tất cả class đều dùng prefix food-*, Minimalism dark theme, responsive
  - JavaScript: IIFE module pattern, State management, Mock data 54 món ăn (3 goal x 3 diet x 3 meal x 2 variants)
  - Logic: Allergy filtering, Budget tier adjustment, Random meal selection

### CSS Classes đã sử dụng (tất cả prefix food-):
- Layout: food-container, food-header, food-quiz-wrapper, food-result-wrapper
- Quiz: food-quiz-group, food-quiz-label, food-option-list, food-option-item, food-option-chip
- Budget: food-budget-input, food-budget-preset, food-budget-unit
- Result: food-result-summary, food-result-tag, food-daily-stats, food-stat-card
- Meals: food-meal-card, food-meal-header, food-meal-title, food-meal-body, food-meal-meta
- Nutrition: food-nutrition-item, food-nutrition-bar, food-nutrition-fill
- Buttons: food-btn-submit, food-btn-refresh, food-btn-reset
- States: food-hidden, food-visible, food-active, food-error, food-fade-in

### Kế hoạch triển khai (cập nhật)
1. [x] Khảo sát cấu trúc dự án
2. [x] Tạo log file
3. [x] Viết HTML/CSS/JS cho food_suggestion.html
4. [x] Kiểm tra và hoàn thiện

## 2026-09-01 22:39 - Cập nhật lần 2: Dark/Light Mode + Tích hợp AI Ollama
- **Trạng thái**: Hoàn thành cập nhật
- **Thay đổi chính**:

### 1. Dark/Light Mode
- Thêm data-theme attribute trên <html> (dark/light)
- CSS variables tách biệt cho 2 themes: --food-bg, --food-card-bg, --food-text-*, --food-border, --food-input-bg
- Toggle UI: sun/moon icons + sliding switch, bo góc, responsive
- Lưu trạng thái vào localStorage('food-theme')
- Transition mượt mà khi chuyển theme (0.25s cubic-bezier)

### 2. Tích hợp API Ollama (AI Food Suggestion)
- Đã đọc và phân tích backend:
  - rag_service.py: process_rag_pipeline() → nhận user_info dict
  - ollama_client.py: generate_chat() → gọi Ollama LLM (llama3.2)
  - prompt_builder.py: Tạo prompt cho LLM chọn món từ Vietnamese_Food_Database.csv
  - exceptions.py: Custom exception classes
- Tạo mới: api/app/main.py (FastAPI endpoint)
  - POST /api/food-suggest: Nhận quiz data → gọi process_rag_pipeline → trả kết quả
  - GET /api/health: Health check Ollama connection
  - CORS middleware cho frontend cross-origin
- Frontend gọi API:
  - CONFIG.API_BASE = 'http://localhost:8000'
  - buildApiPayload(): Map quiz state → API request format
  - callApi(): fetch POST /api/food-suggest với timeout 60s
  - parseApiResponse(): Parse text output từ format_meal_summary() → structured data
  - Fallback: Nếu API offline → sử dụng mock data

### 3. UI States mới
- Loading state: Spinner + text "AI đang phân tích..."
- Error state: Error message + nút "Thử lại"
- Inline loading khi refresh thực đơn

### 4. Mapping quiz values → API fields
- Goal: 'Tăng cơ'/'Giảm cân'/'Cân bằng' → aim (Vietnamese, match rag_service)
- Diet: vegetarian/eatclean/home_cooked → diet_type (match CSV diet_type values)
- Allergies: soy/lactose/seafood → allergen (semicolon-separated)
- Budget → daily_budget
- calories_need & protein_need: Tự tính từ goal (GOAL_NUTRITION map)

### Files đã thay đổi/tạo mới:
- [MODIFIED] food_suggestion.html: Rewrite ~1100 dòng
- [NEW] api/app/main.py: FastAPI app (95 dòng)
- [UPDATED] food_suggestion_log.md

### CSS Classes mới (prefix food-):
- Theme: food-theme-toggle-wrapper, food-theme-toggle, food-theme-switch, food-theme-icon
- Loading: food-loading-wrapper, food-loading-spinner, food-loading-text
- Error: food-error-wrapper, food-error-icon, food-error-detail, food-btn-retry
- Badge: food-header-badge, food-ai-badge
- Ingredients: food-meal-ingredients

### Kế hoạch triển khai (cập nhật lần 2)
1. [x] Khảo sát cấu trúc dự án
2. [x] Tạo log file
3. [x] Viết HTML/CSS/JS v1 (mock data only)
4. [x] Thêm Dark/Light mode
5. [x] Phân tích backend (rag_service, ollama_client, prompt_builder)
6. [x] Tạo FastAPI endpoint (main.py)
7. [x] Tích hợp frontend → API Ollama + fallback mock data
8. [x] Cập nhật log

## 2026-09-01 22:48 - Fix loi npm run dev + Tao package.json
- **Van de**: User chay npm run dev nhung khong co package.json -> loi ENOENT
- **Nguyen nhan**: Du an dung Python FastAPI (backend) + HTML tinh (frontend), chua co cau hinh Node.js
- **Giai phap**:

### Files da tao/sua:
- [NEW] package.json: Cau hinh npm scripts
  - npm run dev: Chay dong thoi backend + frontend (dung concurrently)
  - npm run dev:api: uvicorn api.app.main:app --reload --port 8000
  - npm run dev:frontend: live-server frontend/scr/components --port=5500
  - npm start: Production mode
  - devDependencies: concurrently@^9.0.0, live-server@^1.2.2
- [MODIFIED] .gitignore:
  - Them: node_modules/, package-lock.json
  - Bo: main.py (vi api/app/main.py can duoc track trong git)

### Kiem tra dependencies:
- npm install: OK (216 packages)
- Python packages: fastapi, uvicorn, pydantic deu da cai san

### Cach chay du an:
- cd D:\DOAN-PHU-THINH\FitBreak
- npm run dev
- Backend: http://localhost:8000
- Frontend: http://localhost:5500

## 2026-09-01 22:56 - Chuyen doi trang mac dinh sang AI Food Suggestion
- **Van de**: Khi chay `npm run dev`, trinh duyet tu dong mo `index.html` (la Pomodoro Timer cu) thay vi giao dien Quiz & AI Food Suggestion.
- **Nguyen nhan**: `live-server` mac dinh serve file `index.html` trong thu muc root duoc cau hinh (`frontend/scr/components`).
- **Giai phap**:
  - Doi ten `index.html` cu (Pomodoro Timer) thanh `pomodoro.html` (tam thoi gat sang mot ben theo yeu cau).
  - Doi ten `food_suggestion.html` thanh `index.html` de tro thanh trang chinh mac dinh.
  - Khi chay `npm run dev` hoac mo `http://localhost:5500`, ung dung se hien thi truc tiep giao dien Quiz va AI Food Suggestion.

### Trang thai file hien tai (frontend/scr/components):
- `index.html`: Giao dien Quiz & Goi y thuc don AI (Dark/Light mode, ket noi Ollama qua FastAPI)
- `pomodoro.html`: Pomodoro Timer cu (luu tru doc lap)
- `food_suggestion_log.md`: Nhat ky theo doi qua trinh phat trien

## 2026-09-02 09:53 - Fix loi UnicodeEncodeError khi start server
- **Van de**: Chay `npm run dev` thi server Python bao loi `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'`.
- **Nguyen nhan**: Console cua Windows mac dinh (cp1252) khong the encode cac ki tu emoji nhu `✅` hoac `⚠️` ma toi da de trong file `api/app/main.py`.
- **Giai phap**: Xoa bo emoji va su dung cac ki tu ASCII thong thuong (Vi du: thay bang `[OK]` va `[WARN]`) trong cac lenh print.
- **Ket qua**: Ung dung FastAPI khoi dong thanh cong, loi khong con tai dien.
