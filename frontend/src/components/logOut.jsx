import { useState } from 'react';
import "../style/logOut.css";

const LogOut = ({ onLogoutSuccess }) => {
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/logout', { 
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Đăng xuất thất bại");
      }

      if (onLogoutSuccess) {
        onLogoutSuccess();
      }
    } catch (err) {
      console.error(err.message);
      alert('Không thể đăng xuất: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button" 
      className="log-out-btn" 
      onClick={handleLogout} 
      disabled={loading}
      title="Log out of your session"
    >
      <span className="log-out-icon">⏻</span>
      <span>{loading ? '...' : 'Log Out'}</span>
    </button>
  );
};

export default LogOut;