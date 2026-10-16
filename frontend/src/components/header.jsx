import LogOut from "./logOut";

const Header = ({ user, onLogout, activeTab, onSelectTab }) => {
  const coins = user?.coins || 0;

  const navItems = [
    { id: 'tasks', label: 'Tasks', icon: '⚡' },
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'food', label: 'Food', icon: '🍱' },
    { id: 'schedule', label: 'Schedule', icon: '🗓️' },
    { id: 'team', label: 'Team', icon: '👥' },
    { id: 'shop', label: 'Shop', icon: '⚔️' },
  ];

  return (
    <header className="header">
      <div className="header-logo" onClick={() => onSelectTab('tasks')} style={{ cursor: 'pointer' }}>
        <span>FitBreak</span>
        <span className="header-logo-badge">FITNESS RPG</span>
      </div>

      <nav className="header-nav">
        {navItems.map((item) => (
          <a
            key={item.id}
            href={`#${item.id}`}
            className={activeTab === item.id ? 'active' : ''}
            onClick={(e) => {
              e.preventDefault();
              onSelectTab(item.id);
            }}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <div className="header-stats">
        <div className="header-coin-badge" title="Your current coins">
          <span>🪙</span>
          <span>{coins.toLocaleString()}</span>
        </div>
        <LogOut onLogoutSuccess={onLogout} />
      </div>
    </header>
  );
};

export default Header;