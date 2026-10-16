import { useState } from 'react';
import '../style/createProfile.css';

const CreateProfile = ({ user, onCreateProfileSuccess }) => {
  const [formData, setFormData] = useState({
    name: user?.username || '',
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
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
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
      activity_frequency: Number(formData.activity_frequency)
    };

    try {
      const response = await fetch('http://localhost:8000/profiles/create-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(data.detail[0].msg || 'Dữ liệu nhập vào không hợp lệ!');
        }
        throw new Error(data.detail || data.message || 'Đăng ký thông tin thất bại!');
      }

      if (onCreateProfileSuccess) {
        onCreateProfileSuccess(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-profile-modal-overlay">
      <div className="create-profile-profile-modal">
        <div className="create-profile-profile-modal-header">
          <div className="create-profile-avatar-frame">
            <span className="create-profile-avatar-emoji">🐉</span>
          </div>
          <div className="create-profile-user-stats-summary">
            <h3 className="create-profile-user-display-name">{user?.username || 'Warrior One'}</h3>
            <p className="create-profile-user-subtext">@{user?.email || 'user'} • Level 1 Warrior</p>

            <div className="create-profile-stat-row">
              <span className="create-profile-stat-icon">❤️</span>
              <div className="create-profile-stat-bar-bg">
                <div className="create-profile-stat-bar-fill hp-bar" style={{ width: '88%' }}></div>
              </div>
              <span className="create-profile-stat-value">44 / 50</span>
            </div>

            <div className="create-profile-stat-row">
              <span className="create-profile-stat-icon">⭐</span>
              <div className="create-profile-stat-bar-bg">
                <div className="create-profile-stat-bar-fill xp-bar" style={{ width: '10%' }}></div>
              </div>
              <span className="create-profile-stat-value">0 / 25</span>
            </div>
          </div>
        </div>

        <div className="create-profile-modal-tabs">
          <button className="create-profile-tab-item active">Thiết lập Hồ sơ</button>
          <button className="create-profile-tab-item" type="button" disabled>Chỉ số Stats</button>
          <button className="create-profile-tab-item" type="button" disabled>Thành tựu</button>
        </div>

        <div className="create-profile-modal-body">
          <h2 className="create-profile-form-title">Khởi Tạo Nhân Vật & Hồ Sơ</h2>

          <div className="create-profile-notice-banner">
            Chào mừng bạn! Vui lòng nhập chính xác các thông tin chỉ số bên dưới để hệ thống thiết lập lộ trình nhiệm vụ cá nhân hóa cho bạn.
          </div>

          {error && <div className="create-profile-error-banner">⚠️ {error}</div>}

          <form onSubmit={handleSubmit} className="create-profile-profile-inputs-form">
            <div className="create-profile-form-group">
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

            <div className="create-profile-form-row-2">
              <div className="create-profile-form-group">
                <label>Tuổi (Age)</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  placeholder="Tuổi"
                  required
                />
              </div>

              <div className="create-profile-form-group">
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
            </div>

            <div className="create-profile-form-row-2">
              <div className="create-profile-form-group">
                <label>Chiều cao (cm)</label>
                <input
                  type="number"
                  name="height"
                  value={formData.height}
                  onChange={handleInputChange}
                  placeholder="Chiều cao"
                  required
                />
              </div>

              <div className="create-profile-form-group">
                <label>Cân nặng (kg)</label>
                <input
                  type="number"
                  name="weight"
                  value={formData.weight}
                  onChange={handleInputChange}
                  placeholder="Cân nặng"
                  required
                />
              </div>
            </div>

            <div className="create-profile-form-group">
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

            <div className="create-profile-form-group">
              <label>Tần suất vận động (Activity Frequency)</label>
              <select
                name="activity_frequency"
                value={formData.activity_frequency}
                onChange={handleInputChange}
                required
              >
                <option value="">-- Chọn tần suất vận động --</option>
                <option value="1">Ít vận động / Lâu lâu mới vận động</option>
                <option value="2">Vận động từ 1-4 buổi / tuần</option>
                <option value="3">Vận động từ 5-7 buổi / tuần</option>
              </select>
            </div>

            <div className="create-profile-form-footer">
              <button type="submit" className="create-profile-save-btn" disabled={loading}>
                {loading ? 'Đang lưu...' : 'Lưu Hồ Sơ & Bắt Đầu'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateProfile;