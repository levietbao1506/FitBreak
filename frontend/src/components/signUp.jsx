import { useState } from 'react';
import "../style/signUp.css";

const SignUp = ({ onSignUpSuccess, onGoToLogIn }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/register', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(data.detail[0].msg || 'Dữ liệu nhập vào không hợp lệ!');
        }
        throw new Error(data.detail || data.message || 'Đăng ký thất bại!');
      }

      onSignUpSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-fitbreak-signup-page">
      <div className="signup-fitbreak-content-wrapper">
        <div className="signup-fitbreak-logo-section">
          <div className="signup-badge-hero">NEW WARRIOR ENLISTMENT</div>
          <h1 className="signup-fitbreak-logo">FitBreak</h1>
          <p className="signup-hero-tagline">
            Khởi đầu hành trình gamification thể chất của bạn. Rèn luyện mỗi ngày, nâng cấp nhân vật, và nhận phần thưởng thực tế.
          </p>
          <div className="signup-features-list">
            <div className="signup-feature-item">
              <span className="signup-feature-icon">🛡️</span>
              <span>Tạo nhân vật Avatar pixel art độc bản</span>
            </div>
            <div className="signup-feature-item">
              <span className="signup-feature-icon">📊</span>
              <span>Tự động tính BMI, TDEE và chỉ số dinh dưỡng</span>
            </div>
            <div className="signup-feature-item">
              <span className="signup-feature-icon">🏆</span>
              <span>Tích lũy tiền vàng sắm vũ khí và giáp trụ</span>
            </div>
          </div>
        </div>

        <div className="signup-form-container">
          <div className="signup-form-header">
            <h2>Gia Nhập FitBreak</h2>
            <p>Đăng ký tài khoản miễn phí để khởi tạo chiến binh của bạn</p>
          </div>

          <form className="signup-form" onSubmit={handleSubmit}>
            {error && <div className="signup-error-alert">⚠️ {error}</div>}
            
            <div className="signup-form-group">
              <label htmlFor="email" className="signup-form-label">Email</label>
              <input 
                type="email" 
                id="email" 
                className="signup-form-input" 
                placeholder="tennguoidung@example.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="signup-form-group">
              <label htmlFor="password" className="signup-form-label">Mật khẩu (Password)</label>
              <input 
                type="password" 
                id="password" 
                className="signup-form-input" 
                placeholder="Tối thiểu 6 ký tự"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="signup-form-actions">
              <button type="submit" className="signup-submit-btn" disabled={loading}>
                {loading ? 'Đang khởi tạo...' : 'Tạo Tài Khoản'}
              </button>
              
              <div className="signup-divider-row">
                <span className="divider-line"></span>
                <span className="divider-text">Đã có tài khoản?</span>
                <span className="divider-line"></span>
              </div>

              <button type="button" className="signup-switch-btn" onClick={onGoToLogIn}>
                Đăng Nhập Ngay (Log In)
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignUp;