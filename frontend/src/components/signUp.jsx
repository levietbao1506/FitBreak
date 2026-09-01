import React, { useState } from 'react';

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
    <div className="fitbreak-signup-page">
      <div className="fitbreak-logo-section">
        <h1 className="fitbreak-logo">FitBreak</h1>
      </div>

      <div className="signup-form-container">
        <form className="signup-form" onSubmit={handleSubmit}>
        {error && <p style={{ color: '#ff4d4d', fontSize: '0.85rem', marginBottom: '10px' }}>{error}</p>}
          <div className="form-group">
            <label htmlFor="email" className="form-label">Email</label>
            <input 
              type="email" 
              id="email" 
              className="form-input" 
              placeholder=""
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input 
              type="password" 
              id="password" 
              className="form-input" 
              placeholder=""
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-actions">
            <button type="submit" className="text-button signup-btn" disabled={loading}>
                {loading ? 'Processing...' : 'Sign Up'}
            </button>
            <hr className="divider" />
            <button type="button" className="text-button login-btn" onClick={onGoToLogIn}>
                Log In
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignUp;