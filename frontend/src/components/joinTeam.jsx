import React, { useState, useEffect } from 'react';
import "../style/joinTeam.css"

const JoinTeam = () => {
  const [teamMembers, setTeamMembers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTeamMembers = async () => {
      try {
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
          
          // 🔴 Xử lý bóc tách message lỗi chính xác, tránh [object Object]
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
      } catch (err) {
        setError(err.message || "Đã xảy ra lỗi khi lấy dữ liệu.");
      } finally {
        setLoading(false);
      }
    };

    fetchTeamMembers();
  }, []);

  if (loading) return <div style={{ color: "white" }}>Đang tải dữ liệu...</div>;
  if (error) return <div style={{ color: "red" }}>Lỗi: {error}</div>;
  if (teamMembers.length === 0) return <div style={{ color: "white" }}>Chưa có thành viên nào trong team.</div>;

  return (
    <div className="team-container">
      {/* Thêm tham số index vào hàm map */}
      {teamMembers.map((member, index) => (
        <div key={member.id} className="profile-card">
          
          {/* PHẦN BÊN TRÁI: Số thứ tự */}
          <div className="profile-index">
            {index + 1}
          </div>

          {/* PHẦN BÊN PHẢI: Thông tin user (được bọc lại trong profile-info) */}
          <div className="profile-info">
            <div className="profile-column">
              <ul>
                <li>Name: {member.name}</li>
                <li>Age: {member.age}</li>
                <li>Gender: {member.gender ? "Nam" : "Nữ"}</li>
                <li>Height: {member.height} cm</li>
                <li>Weight: {member.weight} cm</li>
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
  );
};

export default JoinTeam;