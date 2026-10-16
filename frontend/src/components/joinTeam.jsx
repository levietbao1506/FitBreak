import { useState, useEffect } from 'react';
import "../style/joinTeam.css";

const JoinTeam = () => {
  const [teamMembers, setTeamMembers] = useState([]);
  const [emailInput, setEmailInput] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);

  const fetchTeamMembers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      const response = await fetch(`http://localhost:8000/get-team`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        let errorMessage = `Lỗi ${response.status}: Không thể lấy dữ liệu`;
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
          errorMessage = errorData.detail[0].msg || JSON.stringify(errorData.detail);
        } else if (typeof errorData.detail === 'object' && errorData.detail !== null) {
          errorMessage = errorData.detail.message || JSON.stringify(errorData.detail);
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setTeamMembers(Array.isArray(data) ? data : [data]);
      setError(null);
    } catch (err) {
      setError(err.message || "Đã xảy ra lỗi khi lấy dữ liệu.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const handleJoinTeam = async (e) => {
    e.preventDefault();
    if (!emailInput.trim()) {
      alert("Vui lòng nhập email của người chơi!");
      return;
    }

    try {
      setJoining(true);
      const token = localStorage.getItem('token');

      const response = await fetch(`http://localhost:8000/join-team`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ email: emailInput.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Không thể gia nhập team!");
      }

      alert("Tham gia team thành công!");
      setEmailInput('');
      fetchTeamMembers();
    } catch (err) {
      alert(`Lỗi: ${err.message}`);
    } finally {
      setJoining(false);
    }
  };

  return (
    <div className="join-team-wrapper">
      <div className="join-team-header-section">
        <div className="join-title-group">
          <h2>Đội Ngũ Luyện Tập (Team Roster)</h2>
          <p>Mời đồng đội cùng tham gia Guild để cùng hợp sức đánh Boss và tăng sức mạnh!</p>
        </div>

        <form className="join-form" onSubmit={handleJoinTeam}>
          <div className="join-input-box">
            <span className="join-input-icon">✉️</span>
            <input
              type="email"
              className="join-input"
              placeholder="Nhập email đồng đội để gia nhập..."
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
            />
          </div>
          <button type="submit" className="join-btn" disabled={joining}>
            {joining ? "Đang xử lý..." : "Gia nhập Team"}
          </button>
        </form>
      </div>

      {loading ? (
        <div className="team-loading-state">
          <div className="team-spinner"></div>
          <span>Đang tải thông tin đội ngũ...</span>
        </div>
      ) : error ? (
        <div className="team-error-state">
          <span>⚠️ {error}</span>
        </div>
      ) : teamMembers.length === 0 ? (
        <div className="team-empty-state">
          <div className="team-empty-icon">👥</div>
          <h3>Chưa có thành viên nào trong team</h3>
          <p>Nhập email người chơi ở trên để xây dựng Guild ngay!</p>
        </div>
      ) : (
        <div className="team-container">
          {teamMembers.map((member, index) => (
            <div key={member.id || index} className="profile-card">
              <div className="profile-index-badge">
                #{String(index + 1).padStart(2, '0')}
              </div>
              
              <div className="profile-info">
                <div className="profile-header-meta">
                  <h4 className="member-name">{member.name || 'Chiến Binh'}</h4>
                  <span className="member-goal-tag">🎯 {member.goal || 'Tập luyện'}</span>
                </div>

                <div className="profile-details-grid">
                  <div className="profile-detail-column">
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Tuổi:</span>
                      <span className="detail-stat-val">{member.age || '--'}</span>
                    </div>
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Giới tính:</span>
                      <span className="detail-stat-val">{member.gender ? "Nam" : "Nữ"}</span>
                    </div>
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Chiều cao:</span>
                      <span className="detail-stat-val">{member.height} cm</span>
                    </div>
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Cân nặng:</span>
                      <span className="detail-stat-val">{member.weight} kg</span>
                    </div>
                  </div>

                  <div className="profile-detail-column profile-vitals-column">
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Tần suất:</span>
                      <span className="detail-stat-val highlight-val">{member.activity_frequency} buổi/tuần</span>
                    </div>
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Chỉ số BMI:</span>
                      <span className="detail-stat-val">{member.bmi || '--'}</span>
                    </div>
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Năng lượng TDEE:</span>
                      <span className="detail-stat-val">{member.tdee ? `${member.tdee} kcal` : '--'}</span>
                    </div>
                    <div className="detail-stat-row">
                      <span className="detail-stat-label">Protein cần nạp:</span>
                      <span className="detail-stat-val highlight-protein">{member.protein ? `${member.protein}g` : '--'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JoinTeam;