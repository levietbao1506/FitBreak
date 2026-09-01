import React from 'react';

const ProfileBanner = () => {
  return (
    <div className="profile-banner">
      <div className="avatar-box">
        {/* Placeholder cho Avatar */}
        <div className="avatar-pixel"></div>
      </div>
      <div className="user-info">
        <h3>Lê Viết Bảo</h3>
        <p>@tobi1233 • Level 1 Warrior</p>
        
        <div className="progress-bars">
          <div className="bar-container">
            <span className="icon">❤️</span>
            <div className="bar bg-red">
              <div className="fill" style={{ width: '100%' }}></div>
            </div>
            <span className="text">50 / 50</span>
          </div>
          <div className="bar-container">
            <span className="icon">⭐</span>
            <div className="bar bg-yellow">
              <div className="fill" style={{ width: '0%' }}></div>
            </div>
            <span className="text">0 / 25</span>
          </div>
        </div>
      </div>
      <div className="party-promo">
        <h4>Play Habitica with Others</h4>
        <button className="btn-start">Get Started</button>
      </div>
    </div>
  );
};

export default ProfileBanner;