import React, { useState, useEffect } from 'react';
import "../style/foodSuggestForm.css";
import "../style/foodSuggestResult.css";

const initialFormState = {
    calories_need: "",
    protein_need: "",
    daily_budget: "",
    aim: "",
    diet_type: "",
    allergen: ""
};

const FoodSuggest = () => {
    const [formData, setFormData] = useState(initialFormState);
    const [profile, setProfile] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [fetchingProfile, setFetchingProfile] = useState(true);
    const [resultData, setResultData] = useState(null);

    // Fetch dữ liệu profiles của user đăng nhập
    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch('http://localhost:8000/profile', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setProfile(data);
                    
                    // Tự động gán aim ban đầu từ cột goal trong database nếu có
                    if (data.goal) {
                        const goalLower = data.goal.toLowerCase();
                        let mappedGoal = 'Cân bằng';
                        if (goalLower.includes('tăng cơ')) mappedGoal = 'Tăng cơ';
                        else if (goalLower.includes('giảm cân')) mappedGoal = 'Giảm cân';
                        
                        setFormData(prev => ({ ...prev, aim: mappedGoal }));
                    }
                }
            } catch (err) {
                console.error("Lỗi khi tải dữ liệu profile:", err);
            } finally {
                setFetchingProfile(false);
            }
        };

        fetchUserProfile();
    }, []);

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
    
    const DIET_MAP = {
        'Ăn chay': 'vegetarian',
        'Eat clean': 'eatclean',
        'Không kiêng': ''
    };

    const ALLERGEN_MAP = {
        'Đậu nành': 'soy',
        'Lactose': 'lactose',
        'Hải sản': 'seafood'
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        setError(null);
        setLoading(true);
        setResultData(null);

        const rawAllergens = getAllergenArray(formData.allergen);
        const mappedAllergens = rawAllergens
            .map(item => ALLERGEN_MAP[item] || item)
            .join(';');

        // Đưa tdee -> calories_need và protein -> protein_need từ profile vào payload
        const payload = {
            ...formData,
            diet_type: DIET_MAP[formData.diet_type] || formData.diet_type,
            allergen: mappedAllergens,
            calories_need: Number(profile?.tdee) || Number(formData.calories_need) || 0,
            protein_need: Number(profile?.protein) || Number(formData.protein_need) || 0,
            daily_budget: Number(formData.daily_budget) || 0,
        };

        try {
            const response = await fetch('http://localhost:8000/food-suggest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Lỗi khi lấy thực đơn!');
            }

            setResultData(data.result || data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setFormData(initialFormState);
        setResultData(null);
        setError(null);
    };

    return (
    <div className="food-container">
        <header className="food-header">
            <span className="food-header-icon">🍱</span>
            <h1 className="food-header-title">Gợi Ý Thực Đơn AI</h1>
            <div className="food-header-subtitle">Thực đơn cá nhân hóa theo mục tiêu & ngân sách của bạn</div>
        </header>

        {/* Hiển thị thông tin chỉ số đã đồng bộ từ database */}
        {profile && (
            <div style={{ background: '#f0f4f8', padding: '10px 15px', borderRadius: '8px', marginBottom: '15px', fontSize: '14px', color: '#333' }}>
                💡 Chỉ số dinh dưỡng từ hồ sơ: <strong>{profile.tdee} kcal/ngày</strong> | <strong>{profile.protein}g protein/ngày</strong>
            </div>
        )}

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

                <button type="submit" className="food-btn-submit" disabled={!formData.daily_budget || fetchingProfile}>
                    <span>✨</span> Gợi ý thực đơn
                </button>
            </form>
        )}

        {loading && (
            <div className="food-loading-wrapper food-visible food-fade-in">
                <div className="food-loading-spinner"></div>
                <div className="food-loading-text">AI đang phân tích...</div>
                <div className="food-loading-subtext">Đang tạo thực đơn phù hợp cho bạn</div>
            </div>
        )}

        {error && !loading && (
            <div className="food-error-wrapper food-visible food-fade-in">
                <div className="food-error-icon">😥</div>
                <div className="food-error-title">Không thể tạo thực đơn</div>
                <div className="food-error-detail">{error}</div>
                <button className="food-btn-retry" onClick={handleSubmit}>Thử lại</button>
            </div>
        )}

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
                            {Number(formData.daily_budget || 0).toLocaleString()}đ/ngày
                        </span>
                    </div>
                </div>

                <div className="food-daily-stats">
                    <div className="food-stat-card">
                        <div className="food-stat-value">{(resultData.total_calories || 0).toLocaleString()}</div>
                        <div className="food-stat-label">KCAL / NGÀY</div>
                    </div>
                    <div className="food-stat-card">
                        <div className="food-stat-value">{resultData.total_protein || 0}g</div>
                        <div className="food-stat-label">PROTEIN</div>
                    </div>
                    <div className="food-stat-card">
                        <div className="food-stat-value">{(resultData.total_cost || 0).toLocaleString()}đ</div>
                        <div className="food-stat-label">CHI PHÍ</div>
                    </div>
                </div>

                <div className="food-meals-grid">
                    {(resultData.meals || []).map((meal, index) => (
                        <div className="food-meal-card" key={meal.id || index}>
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
                                        <span className="food-meal-meta-value">{meal.kcal || 0} kcal</span>
                                    </div>
                                    <div className="food-meal-meta-item">
                                        <span className="food-meal-meta-icon">💵</span>
                                        <span className="food-meal-meta-value">{(meal.cost || 0).toLocaleString()}đ</span>
                                    </div>
                                </div>

                                <div className="food-meal-nutrition">
                                    <div className="food-nutrition-item">
                                        <div className="food-nutrition-value">{meal.protein || 0}g</div>
                                        <div className="food-nutrition-label">PROTEIN</div>
                                        <div className="food-nutrition-bar"><div className="food-nutrition-fill food-nutrition-fill--protein" style={{width: `${((meal.protein || 0)/50)*100}%`}}></div></div>
                                    </div>
                                    <div className="food-nutrition-item">
                                        <div className="food-nutrition-value">{meal.carbs || 0}g</div>
                                        <div className="food-nutrition-label">CARBS</div>
                                        <div className="food-nutrition-bar"><div className="food-nutrition-fill food-nutrition-fill--carb" style={{width: `${((meal.carbs || 0)/50)*100}%`}}></div></div>
                                    </div>
                                    <div className="food-nutrition-item">
                                        <div className="food-nutrition-value">{meal.fat || 0}g</div>
                                        <div className="food-nutrition-label">FAT</div>
                                        <div className="food-nutrition-bar"><div className="food-nutrition-fill food-nutrition-fill--fat" style={{width: `${((meal.fat || 0)/50)*100}%`}}></div></div>
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