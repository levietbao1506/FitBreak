import React from 'react';
import LogOut from "./logOut";

const Header = ({ user, onLogout, activeTab, onSelectTab }) => {
  const coins = user?.coins || 0;

  return (
    <header className="header">
      <div className="header-logo">FitBreak</div>
      <nav className="header-nav">
        <a 
          href="#tasks" 
          className={activeTab === 'tasks' ? 'active' : ''}
          onClick={(e) => { e.preventDefault(); onSelectTab('tasks'); }}
        >
          Tasks
        </a>
        <a 
          href="#profile" 
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={(e) => { e.preventDefault(); onSelectTab('profile'); }}
        >
          Profile
        </a>
        <a 
          href="#food" 
          className={activeTab === 'food' ? 'active' : ''}
          onClick={(e) => { e.preventDefault(); onSelectTab('food'); }}
        >
          Food
        </a>
        <a 
          href="#schedule" 
          className={activeTab === 'schedule' ? 'active' : ''}
          onClick={(e) => { e.preventDefault(); onSelectTab('schedule'); }}
        >
          Schedule
        </a>
        <a 
          href="#team" 
          className={activeTab === 'team' ? 'active' : ''}
          onClick={(e) => { e.preventDefault(); onSelectTab('team'); }}
        >
          Team
        </a>
        <a href="#">Challenges</a>
        <a href="#">Help</a>
      </nav>
      <div className="header-stats">
        <span>🪙 {coins}</span>
        <LogOut onLogoutSuccess={onLogout} />
      </div>
    </header>
  );
};

export default Header;