import React from 'react';
import LogOut from "./logOut";

const Header = ({ user, onLogout, activeTab, onSelectTab }) => {
  return (
    <header className="header">
      <div className="header-logo">🐉</div>
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
        <a href="#">Shops</a>
        <a href="#">Party</a>
        <a href="#">Group</a>
        <a href="#">Challenges</a>
        <a href="#">Help</a>
      </nav>
      <div className="header-stats">
        <span>💎 0</span>
        <span>🪙 0</span>
        <LogOut onLogoutSuccess={onLogout} />
      </div>
    </header>
  );
};

export default Header;