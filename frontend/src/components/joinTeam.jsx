import React, { useState, useEffect } from 'react';
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
      <form className="join-form" onSubmit={handleJoinTeam}>
        <input
          type="email"
          className="join-input"
          placeholder="Type player’s email to join team"
          value={emailInput}
          onChange={(e) => setEmailInput(e.target.value)}
        />
        <button type="submit" className="join-btn" disabled={joining}>
          {joining ? "..." : "Join"}
        </button>
      </form>
      {loading ? (
        <div style={{ color: "white" }}>Đang tải dữ liệu...</div>
      ) : error ? (
        <div style={{ color: "red" }}>Lỗi: {error}</div>
      ) : teamMembers.length === 0 ? (
        <div style={{ color: "white" }}>Chưa có thành viên nào trong team.</div>
      ) : (
        <div className="team-container">
          {teamMembers.map((member, index) => (
            <div key={member.id || index} className="profile-card">
              <div className="profile-index">
                {index + 1}
              </div>
              <div className="profile-info">
                <div className="profile-column">
                  <ul>
                    <li>Name: {member.name}</li>
                    <li>Age: {member.age}</li>
                    <li>Gender: {member.gender ? "Nam" : "Nữ"}</li>
                    <li>Height: {member.height} cm</li>
                    <li>Weight: {member.weight} kg</li>
                    <li>Goal: {member.goal}</li>
                  </ul>
                </div>
                
                <div className="profile-column">
                  <ul>
                    <li>Activity frequency: {member.activity_frequency} lần/tuần</li>
                    <li>BMI: {member.bmi}</li>
                    <li>BMR: {member.bmr}</li>
                    <li>TDEE: {member.tdee}</li>
                    <li>Protein: {member.protein}g</li>
                  </ul>
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