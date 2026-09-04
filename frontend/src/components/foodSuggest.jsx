import React, { useState } from 'react';
import "../style/foodSuggestForm.css"
import "../style/foodSuggestResult.css"

const initialFormState = {
    calories_need: "",
    daily_budget: "",
    aim: "",
    diet_type: "",
    allergen: "" 
};

const FoodSuggest = () => {
    const [formData, setFormData] = useState(initialFormState);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [resultData, setResultData] = useState(null)

    const getAllergenArray = (allergenStr) => {
    if (!allergenStr) return [];
    return allergenStr.split(';').map(item => item.trim()).filter(Boolean);
  };
    
    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        
        if (type === 'checkbox') {
        setFormData((prev) => {
            const currentList = getAllergenArray(prev.allergen);
            let updatedList;
            
            if (checked) {
            updatedList = [...currentList, value];
            } else {
            updatedList = currentList.filter(item => item !== value);
            }
            
            return { 
            ...prev, 
            allergen: updatedList.join(';')
            };
        });
        } else {
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
        }
    };

    const handleBudgetPreset = (value) => {
        setFormData(prev => ({ ...prev, daily_budget: value }));
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        setResultData(null)

    const payload = {
        ...formData,
        calories_need: Number(formData.calories_need) || 0,
        daily_budget: Number(formData.daily_budget) || 0,
    }

    try {
        // const response = await fetch('http://localhost:8000/food-suggest', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'Authorization': `Bearer ${localStorage.getItem('token')}`,
        //     },
        //     body: JSON.stringify(payload),
        // });

        // const data = await response.json();

        // if (!response.ok) {
        //     if (Array.isArray(data.detail)) {
        //         throw new Error(data.detail[0].msg || 'Dữ liệu nhập vào không hợp lệ!');
        //     }
        //     throw new Error(data.detail || data.message || 'Lỗi khi lấy thực đơn!');
        // }

        // setResultData(data)
        // ------------
        setTimeout(() => {
        setResultData({
          total_calories: 1150,
          total_protein: 60,
          total_cost: 80000,
          meals: [
            {
              id: 1, type: 'Bữa sáng', time: '7:30 - 8:00',
              name: 'Bánh cuốn chả lụa', desc: 'Bánh cuốn nóng, chả lụa, hành phi...',
              kcal: 350, cost: 25000, protein: 15, carbs: 45, fat: 12,
              ingredients: 'Bột gạo, chả lụa, hành phi, nước mắm'
            },
            {
              id: 2, type: 'Bữa trưa', time: '12:00 - 13:00',
              name: 'Bún thịt nướng (phần nhỏ)', desc: 'Bún thịt nướng ít bún, nhiều rau sống.',
              kcal: 450, cost: 30000, protein: 25, carbs: 48, fat: 18,
              ingredients: 'Bún tươi, thịt heo, rau sống, nước mắm pha'
            },
            {
              id: 3, type: 'Bữa tối', time: '18:30 - 19:30',
              name: 'Gỏi cuốn tôm thịt', desc: '3 cuốn gỏi cuốn tôm thịt, rau sống.',
              kcal: 350, cost: 25000, protein: 20, carbs: 38, fat: 10,
              ingredients: 'Bánh tráng, tôm, thịt heo, rau sống, bún'
            }
          ]
        });
        setLoading(false);
      }, 1500);
    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
    };

    const handleReset = () => {
    setResultData(null);
    setFormData(initialFormState);
    setError(null);
  };

    return (
    <div className="food-container">
      <div className="food-theme-toggle-wrapper">
        <div className="food-theme-toggle" role="button" tabIndex={0} aria-label="Chuyển đổi giao diện sáng/tối">
          <span className="food-theme-icon food-theme-icon--sun">☀️</span>
          <div className="food-theme-switch"></div>
          <span className="food-theme-icon food-theme-icon--moon">🌙</span>
        </div>
      </div>

      <header className="food-header">
        <span className="food-header-icon">🍱</span>
        <h1 className="food-header-title">Gợi Ý Thực Đơn AI</h1>
        <div className="food-header-subtitle">Thực đơn cá nhân hóa theo mục tiêu & ngân sách của bạn</div>
      </header>

      {/* HIỂN THỊ FORM KHI KHÔNG LOADING VÀ CHƯA CÓ KẾT QUẢ */}
      {!loading && !resultData && (
        <form className="food-quiz-wrapper food-fade-in" onSubmit={handleSubmit} noValidate>
          <div className="food-quiz-group">
            <div className="food-quiz-label">
              <span className="food-quiz-label-icon">💰</span> Ngân sách mỗi ngày
            </div>
            <div className="food-budget-input-wrapper">
              <input
                type="number"
                name="daily_budget"
                value={formData.daily_budget}
                onChange={handleInputChange}
                className="food-budget-input"
                placeholder="Ví dụ: 80000"
                min="0" step="1000" required
              />
              <span className="food-budget-unit">VNĐ / ngày</span>
            </div>
            <div className="food-budget-presets">
              {['50000', '80000', '120000', '200000'].map(val => (
                <button
                  key={val} type="button"
                  className={`food-budget-preset ${formData.daily_budget === val ? 'food-active' : ''}`}
                  onClick={() => handleBudgetPreset(val)}
                >
                  {Number(val) / 1000}K
                </button>
              ))}
            </div>
          </div>

          <div className="food-quiz-group">
            <div className="food-quiz-label">
              <span className="food-quiz-label-icon">🎯</span> Mục tiêu của bạn
            </div>
            <div className="food-option-list">
              {['Tăng cơ', 'Giảm cân', 'Cân bằng'].map(aim => (
                <label className="food-option-item" key={aim}>
                  <input type="radio" name="aim" value={aim} checked={formData.aim === aim} onChange={handleInputChange} />
                  <span className="food-option-chip">
                    <span className="food-option-chip-icon">{aim === 'Tăng cơ' ? '💪' : aim === 'Giảm cân' ? '🏃' : '⚖️'}</span>
                    {aim}
                  </span>
                </label>
              ))}
            </div>
          </div>
          <div className="food-quiz-group">
            <div className="food-quiz-label">
              <span className="food-quiz-label-icon">🥗</span> Chế độ ăn
            </div>
            <div className="food-option-list">
              {[
                { value: 'Ăn chay', icon: '🌱' },
                { value: 'Eat clean', icon: '🥦' },
                { value: 'Không kiêng', icon: '🍽️' }
              ].map(diet => (
                <label className="food-option-item" key={diet.value}>
                  <input type="radio" name="diet_type" value={diet.value} checked={formData.diet_type === diet.value} onChange={handleInputChange} />
                  <span className="food-option-chip">
                    <span className="food-option-chip-icon">{diet.icon}</span> {diet.value}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="food-quiz-group">
            <div className="food-quiz-label">
              <span className="food-quiz-label-icon">⚠️</span> Dị ứng thực phẩm
            </div>
            <div className="food-quiz-hint">Chọn các loại thực phẩm bạn dị ứng (nếu có)</div>
            <div className="food-option-list">
              {['Đậu nành', 'Lactose', 'Hải sản'].map(allergy => (
                <label className="food-option-item" key={allergy}>
                  <input type="checkbox" name="allergen" value={allergy} checked={formData.allergen.includes(allergy)} onChange={handleInputChange} />
                  <span className="food-option-chip">{allergy}</span>
                </label>
              ))}
            </div>
          </div>

          <button type="submit" className="food-btn-submit" disabled={!formData.daily_budget}>
            <span>✨</span> Gợi ý thực đơn
          </button>
        </form>
      )}

      {/* TRẠNG THÁI LOADING */}
      {loading && (
        <div className="food-loading-wrapper food-visible food-fade-in">
          <div className="food-loading-spinner"></div>
          <div className="food-loading-text">AI đang phân tích...</div>
          <div className="food-loading-subtext">Đang tạo thực đơn phù hợp cho bạn</div>
        </div>
      )}

      {/* TRẠNG THÁI LỖI */}
      {error && !loading && (
        <div className="food-error-wrapper food-visible food-fade-in">
          <div className="food-error-icon">😥</div>
          <div className="food-error-title">Không thể tạo thực đơn</div>
          <div className="food-error-detail">{error}</div>
          <button className="food-btn-retry" onClick={handleSubmit}>Thử lại</button>
        </div>
      )}

      {/* TRẠNG THÁI KẾT QUẢ */}
      {resultData && !loading && (
        <div className="food-result-wrapper food-visible food-fade-in">
          <div className="food-result-summary">
            <div className="food-result-summary-title">
              <span>📋</span> Thực đơn của bạn
            </div>
            <div className="food-result-tags">
              {formData.aim && <span className="food-result-tag food-result-tag--goal">{formData.aim}</span>}
              {formData.diet_type && <span className="food-result-tag food-result-tag--diet">{formData.diet_type}</span>}
              <span className="food-result-tag food-result-tag--budget">
                {Number(formData.daily_budget).toLocaleString()}đ/ngày
              </span>
            </div>
          </div>

          <div className="food-daily-stats">
            <div className="food-stat-card">
              <div className="food-stat-value">{resultData.total_calories.toLocaleString()}</div>
              <div className="food-stat-label">KCAL / NGÀY</div>
            </div>
            <div className="food-stat-card">
              <div className="food-stat-value">{resultData.total_protein}g</div>
              <div className="food-stat-label">PROTEIN</div>
            </div>
            <div className="food-stat-card">
              <div className="food-stat-value">{resultData.total_cost.toLocaleString()}đ</div>
              <div className="food-stat-label">CHI PHÍ</div>
            </div>
          </div>

          <div className="food-meals-grid">
            {resultData.meals.map(meal => (
              <div className="food-meal-card" key={meal.id}>
                <div className="food-meal-header">
                  <div className="food-meal-title">
                    <span className="food-meal-title-icon">{meal.type === 'Bữa sáng' ? '🌅' : meal.type === 'Bữa trưa' ? '🌞' : '🌙'}</span>
                    {meal.type}
                  </div>
                  <div className="food-meal-time">{meal.time}</div>
                </div>
                
                <div className="food-meal-body">
                  <div className="food-meal-name">{meal.name}</div>
                  <div className="food-meal-description">{meal.desc}</div>
                  
                  <div className="food-meal-meta">
                    <div className="food-meal-meta-item">
                      <span className="food-meal-meta-icon">🔥</span>
                      <span className="food-meal-meta-value">{meal.kcal} kcal</span>
                    </div>
                    <div className="food-meal-meta-item">
                      <span className="food-meal-meta-icon">💵</span>
                      <span className="food-meal-meta-value">{meal.cost.toLocaleString()}đ</span>
                    </div>
                  </div>

                  <div className="food-meal-nutrition">
                    <div className="food-nutrition-item">
                      <div className="food-nutrition-value">{meal.protein}g</div>
                      <div className="food-nutrition-label">PROTEIN</div>
                      <div className="food-nutrition-bar"><div className="food-nutrition-fill food-nutrition-fill--protein" style={{width: `${(meal.protein/50)*100}%`}}></div></div>
                    </div>
                    <div className="food-nutrition-item">
                      <div className="food-nutrition-value">{meal.carbs}g</div>
                      <div className="food-nutrition-label">CARBS</div>
                      <div className="food-nutrition-bar"><div className="food-nutrition-fill food-nutrition-fill--carb" style={{width: `${(meal.carbs/50)*100}%`}}></div></div>
                    </div>
                    <div className="food-nutrition-item">
                      <div className="food-nutrition-value">{meal.fat}g</div>
                      <div className="food-nutrition-label">FAT</div>
                      <div className="food-nutrition-bar"><div className="food-nutrition-fill food-nutrition-fill--fat" style={{width: `${(meal.fat/50)*100}%`}}></div></div>
                    </div>
                  </div>

                  <div className="food-meal-ingredients">
                    <strong>Nguyên liệu:</strong> {meal.ingredients}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="food-result-actions">
            <button className="food-btn-refresh" onClick={handleSubmit}>
              <span>🔄</span> Đổi thực đơn khác
            </button>
            <button className="food-btn-reset" onClick={handleReset}>
              <span>↩️</span> Làm lại quiz
            </button>
          </div>
        </div>
      )}
    </div>
    );
};

export default FoodSuggest;