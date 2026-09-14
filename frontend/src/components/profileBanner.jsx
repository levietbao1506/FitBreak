import React, { useEffect, useState } from 'react';
import AvatarDisplay from './avatarDisplay';
import '../style/profileBanner.css';

const API_BASE_URL = 'http://localhost:8000';

const ProfileBanner = ({ user, teamName, token: propToken, avatarVersion }) => {
  const name = user?.name || "Player 1";
  const email = user?.email || "player1@gmail.com";
  const damage = user?.damage ?? user?.str ?? 1;
  const coins = user?.coins ?? 0;

  const activeTeam = user?.team || teamName || 1;
  const token = propToken || localStorage.getItem('token');
  const userId = user?.id || user?.user_id;

  const [equippedUrls, setEquippedUrls] = useState({});
  const [boss, setBoss] = useState({
    boss_name: "Loading...",
    health: 100,
    max_health: 100,
    reward_coins: 10,
    image_url: ""
  });

  useEffect(() => {
    const fetchData = async () => {
      if (!token) return;

      const headers = { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      try {
        const resBoss = await fetch(`${API_BASE_URL}/get-raid-boss/${activeTeam}`, { headers });
        if (resBoss.ok) {
          const bossData = await resBoss.json();
          setBoss(bossData);
        }

        if (userId) {
          const resAvatar = await fetch(`${API_BASE_URL}/user/equipped-avatar/${userId}`, { headers });
          if (resAvatar.ok) {
            const avatarUrls = await resAvatar.json();
            setEquippedUrls(avatarUrls);
          }
        }
      } catch (err) {
        console.error("Lỗi tải dữ liệu Profile Banner:", err);
      }
    };

    fetchData();
  }, [activeTeam, token, userId, avatarVersion]); // Tự gọi lại khi avatarVersion thay đổi

  const healthPercentage = Math.max(0, Math.min(100, (boss.health / boss.max_health) * 100));

  return (
    <div className="profile-banner">
      {/* Khung avatar kích thước 110px x 110px, bo tròn không bị góc thừa */}
      <div className="avatar-box" style={{ width: '150px', height: '150px', flexShrink: 0, borderRadius: '12px', overflow: 'hidden' }}>
        <AvatarDisplay equippedItems={equippedUrls} />
      </div>
      
      <div className="user-info">
        <h3>{name}</h3>
        <p>{email}</p>
        
        <div className="user-stats-text">
          <div>
            <span style={{ marginRight: '8px' }}>⚔️</span>
            <span>{damage} DMG</span>
          </div>
          <div>
            <span style={{ marginRight: '8px' }}>🪙</span>
            <span>{coins} Coins</span>
          </div>
        </div>
      </div>

      <div className="boss-section">
        <div className="boss-avatar">
          {boss.image_url ? (
            <img src={boss.image_url} alt={boss.boss_name} />
          ) : (
            <div className="boss-placeholder">👾</div>
          )}
        </div>
        
        <div className="boss-details">
          <div className="boss-header">
            <span className="boss-title">Boss: {boss.boss_name}</span>
            <span className="boss-reward">🪙 +{boss.reward_coins} Coins</span>
          </div>
          
          <div className="boss-hp-container">
            <div className="boss-hp-bar">
              <div 
                className="boss-hp-fill" 
                style={{ width: `${healthPercentage}%` }}
              ></div>
            </div>
            <span className="boss-hp-text">{boss.health} / {boss.max_health} HP</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileBanner;