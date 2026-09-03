import React, { useState } from 'react';
import "../style/logIn.css"

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
      <div className="login-fitbreak-logo-section">
        <h1 className="login-fitbreak-logo">FitBreak</h1>
      </div>

      <div className="login-form-container">
        <form className="login-form" onSubmit={handleSubmit}>
          {error && <p style={{ color: '#ff4d4d', fontSize: '0.85rem', marginBottom: '10px' }}>{error}</p>}
          <div className="login-form-group">
            <label htmlFor="email" className="login-form-label">Email</label>
            <input 
              type="email" 
              id="email" 
              className="login-form-input" 
              placeholder=""
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="login-form-group">
            <label htmlFor="password" className="login-form-label">Password</label>
            <input 
              type="password" 
              id="password" 
              className="login-form-input" 
              placeholder=""
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="login-form-actions">
            <button type="submit" className="login-text-button log-in-btn" disabled={loading}>
                {loading ? 'Processing...' : 'Log In'}
            </button>
            <hr className="login-divider" />
            <button type="button" className="login-text-button sign-up-btn" onClick={onGoToSignUp}>
              Sign Up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LogIn;