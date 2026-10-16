import { useState } from 'react';
import "../style/logIn.css";

const LogIn = ({ onLoginSuccess, onGoToSignUp }) => {
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
      const response = await fetch('http://localhost:8000/login', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(data.detail[0].msg || 'Dữ liệu nhập vào không hợp lệ!');
        }
        throw new Error(data.detail || data.message || 'Đăng nhập thất bại!');
      }

      onLoginSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-fitbreak-login-page">
      <div className="login-fitbreak-content-wrapper">
        <div className="login-fitbreak-logo-section">
          <div className="login-badge-hero">FITNESS RPG PLATFORM</div>
          <h1 className="login-fitbreak-logo">FitBreak</h1>
          <p className="login-hero-tagline">
            Biến mỗi đợt nghỉ ngơi thành sức mạnh. Vận động, đánh Boss cùng đồng đội và nâng tầm thể lực mỗi ngày.
          </p>
          <div className="login-features-list">
            <div className="feature-item">
              <span className="feature-icon">⚔️</span>
              <span>Chiến Boss Raid nhận vàng & trang bị</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">⏰</span>
              <span>Đồng hồ Pomodoro nhắc nhở vận động</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🍱</span>
              <span>Thực đơn dinh dưỡng cá nhân hóa bằng AI</span>
            </div>
          </div>
        </div>

        <div className="login-form-container">
          <div className="login-form-header">
            <h2>Chào Mừng Trở Lại!</h2>
            <p>Đăng nhập vào tài khoản của bạn để tiếp tục chuỗi nhiệm vụ</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            {error && <div className="login-error-alert">⚠️ {error}</div>}
            
            <div className="login-form-group">
              <label htmlFor="email" className="login-form-label">Email</label>
              <input 
                type="email" 
                id="email" 
                className="login-form-input" 
                placeholder="tennguoidung@example.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="login-form-group">
              <label htmlFor="password" className="login-form-label">Mật khẩu (Password)</label>
              <input 
                type="password" 
                id="password" 
                className="login-form-input" 
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="login-form-actions">
              <button type="submit" className="login-submit-btn" disabled={loading}>
                {loading ? 'Đang xác thực...' : 'Đăng Nhập'}
              </button>
              
              <div className="login-divider-row">
                <span className="divider-line"></span>
                <span className="divider-text">Chưa có tài khoản?</span>
                <span className="divider-line"></span>
              </div>

              <button type="button" className="login-switch-btn" onClick={onGoToSignUp}>
                Tạo tài khoản mới (Sign Up)
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LogIn;