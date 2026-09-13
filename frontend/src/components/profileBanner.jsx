import React, { useEffect, useState } from 'react';
import '../style/profileBanner.css';

const API_BASE_URL = 'http://localhost:8000';

const ProfileBanner = ({ user, teamName, token: propToken }) => {
  const name = user?.name || "Player 1";
  const email = user?.email || "player1@gmail.com";
  const damage = user?.damage ?? user?.str ?? 1;
  const coins = user?.coins ?? 0;

  const activeTeam = user?.team || teamName || 1;
  const token = propToken || localStorage.getItem('token');

  const [boss, setBoss] = useState({
    boss_name: "Loading...",
    health: 100,
    max_health: 100,
    reward_coins: 10,
    image_url: ""
  });

  useEffect(() => {
    const fetchBossData = async () => {
      if (!token) return;

      try {
        const res = await fetch(`${API_BASE_URL}/get-raid-boss/${activeTeam}`, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (res.ok) {
          const data = await res.json();
          setBoss(data);
        } else {
          console.error("Lỗi API Backend:", res.status);
        }
      } catch (err) {
        console.error("Lỗi lấy thông tin Boss:", err);
      }
    };

    fetchBossData();
  }, [activeTeam, token]);

  const healthPercentage = Math.max(0, Math.min(100, (boss.health / boss.max_health) * 100));

  return (
    <div className="profile-banner">
      <div className="avatar-box">
        <div className="avatar-pixel"></div>
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