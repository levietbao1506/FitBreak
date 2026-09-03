import React, { useState } from 'react';
import "../style/updateProfile.css"

const UpdateProfile = ({ onUpdateProfileSuccess }) => {
    const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    height: '',
    weight: '',
    goal: '',
    activityFrequency: '',
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null)
    setLoading(null)

    const payload = {
      ...formData,
      gender: formData.gender === 'true',
      age: Number(formData.age),
      height: Number(formData.height),
      weight: Number(formData.weight),
      activity_frequency: Number(formData.activity_frequency)
    }

    try {
      const response = await fetch('http://localhost:8000/profiles/update-profile', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
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

      onUpdateProfileSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="update-profile-profile-form-container">
        {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit} className="update-profile-profile-form">
        <div className="update-profile-form-content">  
          <div className="update-profile-form-column">
            <div className="update-profile-form-group">
              <label> Display Name :</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Nhập tên hiển thị"
                required
              />
            </div>
            <div className="update-profile-form-group">
              <label>Age :</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                placeholder="Tuổi"
                required
              />
            </div>
            <div className="update-profile-form-group">
              <label>Gender :</label>
              <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">-- Chọn giới tính --</option>
                  <option value="true">Nam</option>
                  <option value="false">Nữ</option>
                </select>
            </div>
            <div className="update-profile-form-group">
              <label>Height :</label>
              <input
                type="text"
                name="height"
                value={formData.height}
                onChange={handleInputChange}
              />
            </div>
            <div className="update-profile-form-group">
              <label>Weight :</label>
              <input
                type="text"
                name="weight"
                value={formData.weight}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="update-profile-form-column">
            <div className="update-profile-form-group">
              <label>Goal :</label>
              <select
                name="goal"
                value={formData.goal}
                onChange={handleInputChange}
                required
              >
                <option value="">-- Chọn mục tiêu --</option>
                <option value="giảm cân"> Giảm cân </option>
                <option value="cân bằng"> Cân bằng </option>
                <option value="tăng cơ"> Tăng cơ </option>
              </select>
            </div>
            <div className="update-profile-form-group">
              <label>Activity Frequency :</label>
              <select
                name="activity_frequency"
                value={formData.activity_frequency}
                onChange={handleInputChange}
                required
              >
                <option value="">-- Chọn tần suất vận động --</option>
                <option value="1"> Ít vận động / Lâu lâu mới vận động </option>
                <option value="2"> Vận động từ 1-3 buổi/tuần </option>
                <option value="3"> Vận động từ 4-5 buổi một/tuần </option>
                <option value="4"> Vận động 6-7 buổi/tuần </option>
              </select>
            </div>
          </div>
        </div>
        
        <button type="submit" className="update-profile-save-button" disabled={loading}>
            {loading ? 'Đang lưu...' : 'Save'}
        </button>
      </form>
    </div>
  );
};

export default UpdateProfile;