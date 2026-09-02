import React from 'react';
import LogOut from "./logOut";

const Header = ({ user, onLogout }) => {
  return (
    <header className="header">
      <div className="header-logo">🐉</div>
      <nav className="header-nav">
        <a href="#" className="active">Tasks</a>
        <a href="#">Profile</a>
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