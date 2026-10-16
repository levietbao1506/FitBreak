import { useState } from 'react';
import "../style/updateProfile.css";

const UpdateProfile = ({ onUpdateProfileSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    height: '',
    weight: '',
    goal: '',
    activity_frequency: '',
  });

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const payload = {
      ...formData,
      gender: formData.gender === 'true',
      age: Number(formData.age),
      height: Number(formData.height),
      weight: Number(formData.weight),
      activity_frequency: Number(formData.activity_frequency),
    };

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

      onUpdateProfileSuccess(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="update-profile-profile-form-container">
      <div className="update-profile-header">
        <span className="update-profile-badge">PROFILE SETTINGS</span>
        <h2>Cập Nhật Hồ Sơ & Thể Trạng</h2>
        <p>Cập nhật số đo và tần suất hoạt động để hệ thống điều chỉnh độ khó và bài tập phù hợp</p>
      </div>

      <form onSubmit={handleSubmit} className="update-profile-profile-form">
        {error && (
          <div className="update-profile-error-box">
            <span>⚠️ {error}</span>
          </div>
        )}
        
        <div className="update-profile-card">
          <div className="update-profile-form-content">
            <div className="update-profile-form-column">
              <div className="update-profile-form-group">
                <label>Tên hiển thị (Display Name)</label>
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
                <label>Tuổi (Age)</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  placeholder="Tuổi của bạn"
                  required
                />
              </div>

              <div className="update-profile-form-group">
                <label>Giới tính (Gender)</label>
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
                <label>Chiều cao (cm)</label>
                <input
                  type="number"
                  name="height"
                  value={formData.height}
                  onChange={handleInputChange}
                  placeholder="Ví dụ: 175"
                />
              </div>
            </div>

            <div className="update-profile-form-column">
              <div className="update-profile-form-group">
                <label>Cân nặng (kg)</label>
                <input
                  type="number"
                  name="weight"
                  value={formData.weight}
                  onChange={handleInputChange}
                  placeholder="Ví dụ: 68"
                />
              </div>

              <div className="update-profile-form-group">
                <label>Mục tiêu rèn luyện (Goal)</label>
                <select
                  name="goal"
                  value={formData.goal}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">-- Chọn mục tiêu --</option>
                  <option value="giảm cân">Giảm cân</option>
                  <option value="cân bằng">Cân bằng</option>
                  <option value="tăng cơ">Tăng cơ</option>
                </select>
              </div>

              <div className="update-profile-form-group">
                <label>Tần suất vận động (Activity Frequency)</label>
                <select
                  name="activity_frequency"
                  value={formData.activity_frequency}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">-- Chọn tần suất --</option>
                  <option value="1">Ít vận động / Lâu lâu mới vận động</option>
                  <option value="2">Vận động từ 1-4 buổi / tuần</option>
                  <option value="3">Vận động từ 5-7 buổi / tuần</option>
                </select>
              </div>
            </div>
          </div>

          <div className="update-profile-actions">
            <button type="submit" className="update-profile-save-button" disabled={loading}>
              {loading ? 'Đang lưu...' : 'Lưu Thay Đổi'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default UpdateProfile;