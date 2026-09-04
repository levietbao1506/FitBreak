import React, { useState } from 'react';
import "../style/profileInformation.css";

const ProfileInformation = ({ onUpdateProfileSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: 'Nam',
    height: '',
    weight: '',
    goal: '',
    activityFrequency: '1',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Vui lòng đăng nhập trước khi cập nhật hồ sơ!');
      }

      const isMale = formData.gender === 'Nam' || formData.gender === 'male' || formData.gender === 'true';

      const payload = {
        name: formData.name.trim(),
        age: parseInt(formData.age, 10) || 0,
        gender: isMale,
        height: parseInt(formData.height, 10) || 0,
        weight: parseInt(formData.weight, 10) || 0,
        goal: formData.goal.trim(),
        activity_frequency: parseInt(formData.activityFrequency, 10) || 1,
      };

      if (!payload.name || payload.age <= 0 || payload.height <= 0 || payload.weight <= 0) {
        throw new Error('Vui lòng điền đầy đủ và chính xác thông tin tuổi, chiều cao, cân nặng!');
      }

      const response = await fetch('http://localhost:8000/profiles/update-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(data.detail[0].msg || 'Dữ liệu nhập vào không hợp lệ!');
        }
        throw new Error(data.detail || data.message || 'Cập nhật thông tin thất bại!');
      }

      if (onUpdateProfileSuccess) {
        onUpdateProfileSuccess(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-form-container">
      <form onSubmit={handleSubmit} className="profile-form">
        {error && (
          <p style={{ color: '#ff4d4d', fontSize: '0.85rem', marginBottom: '10px' }}>
            {error}
          </p>
        )}
        <div className="form-content">
          <div className="form-column">
            <div className="form-group">
              <label>Họ và tên:</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Tuổi:</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                min="1"
                required
              />
            </div>
            <div className="form-group">
              <label>Giới tính:</label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
              >
                <option value="Nam">Nam</option>
                <option value="Nữ">Nữ</option>
              </select>
            </div>
            <div className="form-group">
              <label>Chiều cao (cm):</label>
              <input
                type="number"
                name="height"
                value={formData.height}
                onChange={handleInputChange}
                min="50"
                max="250"
                required
              />
            </div>
            <div className="form-group">
              <label>Cân nặng (kg):</label>
              <input
                type="number"
                name="weight"
                value={formData.weight}
                onChange={handleInputChange}
                min="20"
                max="300"
                required
              />
            </div>
          </div>

          <div className="form-column">
            <div className="form-group">
              <label>Mục tiêu thể hình:</label>
              <input
                type="text"
                name="goal"
                placeholder="Tăng cơ, Giảm cân, Cân bằng..."
                value={formData.goal}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Mức độ vận động:</label>
              <select
                name="activityFrequency"
                value={formData.activityFrequency}
                onChange={handleInputChange}
              >
                <option value="1">1: Ít vận động / Ngồi nhiều</option>
                <option value="2">2: Vận động vừa (1 - 4 buổi / tuần)</option>
                <option value="3">3: Vận động nhiều (5 - 6 buổi / tuần)</option>
              </select>
            </div>
          </div>
        </div>

        <button type="submit" className="save-button" disabled={loading}>
          {loading ? 'Đang lưu...' : 'Lưu thông tin'}
        </button>
      </form>
    </div>
  );
};

export default ProfileInformation;