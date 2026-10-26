import { useState, useEffect } from 'react';
import "../style/updateProfile.css";

const UpdateProfile = ({ user, onUpdateProfileSuccess }) => {
  const [formData, setFormData] = useState({
    name: user?.name || '',
    age: user?.age ? String(user.age) : '',
    gender: user?.gender !== undefined ? String(user.gender) : '',
    height: user?.height ? String(user.height) : '',
    weight: user?.weight ? String(user.weight) : '',
    goal: user?.goal || '',
    activity_frequency: user?.activity_frequency ? String(user.activity_frequency) : '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        age: user.age ? String(user.age) : '',
        gender: user.gender !== undefined ? String(user.gender) : '',
        height: user.height ? String(user.height) : '',
        weight: user.weight ? String(user.weight) : '',
        goal: user.goal || '',
        activity_frequency: user.activity_frequency ? String(user.activity_frequency) : '',
      });
    }
  }, [user]);

  const [medicalData, setMedicalData] = useState({
    sys: '',
    dia: '',
    glycemic_index: '',
    time: 0, // 0: Lúc đói, 1: Trước bữa ăn, 2: Ngẫu nhiên
    spo2_index: '',
  });

  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const [medicalResult, setMedicalResult] = useState(null);
  const [medicalLoading, setMedicalLoading] = useState(false);
  const [medicalError, setMedicalError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleMedicalInputChange = (e) => {
    const { name, value } = e.target;
    setMedicalData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleTimeSelect = (val) => {
    setMedicalData((prev) => ({
      ...prev,
      time: val,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
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

      setSuccessMsg('Cập nhật hồ sơ thành công!');
      onUpdateProfileSuccess(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMedicalCheckup = async () => {
    setMedicalError(null);
    setMedicalLoading(true);

    const payload = {
      weight: formData.weight ? Number(formData.weight) : null,
      height: formData.height ? Number(formData.height) : null,
      sys: medicalData.sys ? Number(medicalData.sys) : null,
      dia: medicalData.dia ? Number(medicalData.dia) : null,
      time: medicalData.glycemic_index ? Number(medicalData.time) : null,
      glycemic_index: medicalData.glycemic_index ? Number(medicalData.glycemic_index) : null,
      spo2_index: medicalData.spo2_index ? Number(medicalData.spo2_index) : null,
    };

    try {
      const response = await fetch('http://localhost:8000/profiles/medical-checkup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Không thể phân tích chỉ số y tế');
      }

      setMedicalResult(data.result);
    } catch (err) {
      setMedicalError(err.message);
    } finally {
      setMedicalLoading(false);
    }
  };

  const getBadgeClass = (level) => {
    switch (level) {
      case 'good': return 'med-badge-good';
      case 'warning': return 'med-badge-warning';
      case 'danger': return 'med-badge-danger';
      case 'critical': return 'med-badge-critical';
      default: return '';
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
        {successMsg && (
          <div className="update-profile-success-box">
            <span>✅ {successMsg}</span>
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

      {/* MEDICAL CHECKUP SECTION */}
      <div className="medical-checkup-container">
        <div className="update-profile-header">
          <span className="medical-badge">HEALTH & MEDICAL CHECKUP</span>
          <h2>Đo Lường & Đánh Giá Chỉ Số Sức Khỏe Tại Nhà</h2>
          <p>
            Nhập các chỉ số đo được từ thiết bị của bạn (tùy chọn theo máy bạn có).
            Chiều cao và cân nặng sẽ tự động đồng bộ từ hồ sơ bên trên.
          </p>
        </div>

        {medicalError && (
          <div className="update-profile-error-box">
            <span>⚠️ {medicalError}</span>
          </div>
        )}

        <div className="medical-device-card">
          {/* Row 1: Máy đo huyết áp */}
          <div className="medical-device-row">
            <div className="medical-device-header">
              <div className="device-icon-box">🩺</div>
              <div>
                <h4>Máy đo huyết áp</h4>
                <p className="device-subtitle">Đo huyết áp tâm thu (SYS) và tâm trương (DIA) (mmHg)</p>
              </div>
            </div>
            <div className="device-inputs-grid">
              <div className="update-profile-form-group">
                <label>Huyết áp tâm thu (SYS - chỉ số trên)</label>
                <input
                  type="number"
                  name="sys"
                  value={medicalData.sys}
                  onChange={handleMedicalInputChange}
                  placeholder="Ví dụ: 120"
                />
              </div>
              <div className="update-profile-form-group">
                <label>Huyết áp tâm trương (DIA - chỉ số dưới)</label>
                <input
                  type="number"
                  name="dia"
                  value={medicalData.dia}
                  onChange={handleMedicalInputChange}
                  placeholder="Ví dụ: 80"
                />
              </div>
            </div>
          </div>

          {/* Row 2: Máy đo đường huyết */}
          <div className="medical-device-row">
            <div className="medical-device-header">
              <div className="device-icon-box">🩸</div>
              <div>
                <h4>Máy đo đường huyết</h4>
                <p className="device-subtitle">Đo nồng độ đường trong máu (mg/dL) kèm thời điểm đo</p>
              </div>
            </div>
            <div className="device-inputs-grid">
              <div className="update-profile-form-group">
                <label>Chỉ số đường huyết (mg/dL)</label>
                <input
                  type="number"
                  name="glycemic_index"
                  value={medicalData.glycemic_index}
                  onChange={handleMedicalInputChange}
                  placeholder="Ví dụ: 95"
                />
              </div>
              <div className="update-profile-form-group">
                <label>Thời điểm lúc đo đường huyết</label>
                <div className="time-select-chips">
                  {[
                    { val: 0, label: "Lúc đói (≥ 8h)" },
                    { val: 1, label: "Trước bữa ăn" },
                    { val: 2, label: "Ngẫu nhiên" },
                  ].map((item) => (
                    <button
                      key={item.val}
                      type="button"
                      className={`time-chip ${medicalData.time === item.val ? 'active' : ''}`}
                      onClick={() => handleTimeSelect(item.val)}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Row 3: Máy đo nồng độ oxy trong máu */}
          <div className="medical-device-row">
            <div className="medical-device-header">
              <div className="device-icon-box">🫁</div>
              <div>
                <h4>Máy đo nồng độ oxy (SpO2)</h4>
                <p className="device-subtitle">Đo độ bão hòa oxy trong máu (%) kẹp đầu ngón tay</p>
              </div>
            </div>
            <div className="device-inputs-grid single-input">
              <div className="update-profile-form-group">
                <label>Chỉ số SpO2 (%)</label>
                <input
                  type="number"
                  name="spo2_index"
                  value={medicalData.spo2_index}
                  onChange={handleMedicalInputChange}
                  placeholder="Ví dụ: 98"
                />
              </div>
            </div>
          </div>

          <div className="medical-action-bar">
            <button
              type="button"
              className="medical-analyze-btn"
              onClick={handleMedicalCheckup}
              disabled={medicalLoading}
            >
              {medicalLoading ? 'Đang phân tích...' : '🩺 Đánh Giá Rủi Ro Sức Khỏe & Cá Nhân Hóa'}
            </button>
          </div>
        </div>

        {/* MEDICAL RESULTS DISPLAY */}
        {medicalResult && (
          <div className="medical-results-box">
            <div className="results-header">
              <h3>📊 Kết Quả Đánh Giá Sức Khỏe & Rủi Ro</h3>
              <p>Phân tích tự động dựa trên chỉ số bạn đã cung cấp</p>
            </div>

            <div className="status-cards-grid">
              {medicalResult.details?.bmi && (
                <div className="status-card">
                  <div className="status-card-header">
                    <span className="status-name">Thể trạng (BMI)</span>
                    <span className={`status-badge ${getBadgeClass(medicalResult.details.bmi.level)}`}>
                      {medicalResult.details.bmi.status}
                    </span>
                  </div>
                  <div className="status-value">{medicalResult.details.bmi.value} kg/m²</div>
                  <p className="status-risk">{medicalResult.details.bmi.risk}</p>
                </div>
              )}

              {medicalResult.details?.blood_pressure && (
                <div className="status-card">
                  <div className="status-card-header">
                    <span className="status-name">Huyết áp</span>
                    <span className={`status-badge ${getBadgeClass(medicalResult.details.blood_pressure.level)}`}>
                      {medicalResult.details.blood_pressure.status}
                    </span>
                  </div>
                  <div className="status-value">
                    {medicalResult.details.blood_pressure.sys} / {medicalResult.details.blood_pressure.dia} mmHg
                  </div>
                  <p className="status-risk">{medicalResult.details.blood_pressure.risk}</p>
                </div>
              )}

              {medicalResult.details?.diabete && (
                <div className="status-card">
                  <div className="status-card-header">
                    <span className="status-name">Đường huyết</span>
                    <span className={`status-badge ${getBadgeClass(medicalResult.details.diabete.level)}`}>
                      {medicalResult.details.diabete.status}
                    </span>
                  </div>
                  <div className="status-value">{medicalResult.details.diabete.value} mg/dL</div>
                  <p className="status-risk">{medicalResult.details.diabete.risk}</p>
                </div>
              )}

              {medicalResult.details?.spo2 && (
                <div className="status-card">
                  <div className="status-card-header">
                    <span className="status-name">Nồng độ SpO2</span>
                    <span className={`status-badge ${getBadgeClass(medicalResult.details.spo2.level)}`}>
                      {medicalResult.details.spo2.status}
                    </span>
                  </div>
                  <div className="status-value">{medicalResult.details.spo2.value} %</div>
                  <p className="status-risk">{medicalResult.details.spo2.risk}</p>
                </div>
              )}
            </div>

            {/* ADVICES SECTION */}
            <div className="advice-sections">
              {medicalResult.recommendations?.workout_advice?.length > 0 && (
                <div className="advice-card workout-advice">
                  <h4>🏋️ Cá Nhân Hóa Lịch Tập Theo Thể Trạng</h4>
                  <ul>
                    {medicalResult.recommendations.workout_advice.map((adv, idx) => (
                      <li key={idx}>{adv}</li>
                    ))}
                  </ul>
                </div>
              )}

              {medicalResult.recommendations?.diet_advice?.length > 0 && (
                <div className="advice-card diet-advice">
                  <h4>🥗 Lời Khuyên Dinh Dưỡng & Thực Đơn AI</h4>
                  <ul>
                    {medicalResult.recommendations.diet_advice.map((adv, idx) => (
                      <li key={idx}>{adv}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UpdateProfile;
