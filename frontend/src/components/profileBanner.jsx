import React, { useEffect, useState, useCallback } from 'react';
import AvatarDisplay from './avatarDisplay';
import '../style/profileBanner.css';

const API_BASE_URL = 'http://localhost:8000';

const ProfileBanner = ({ user, teamName, token: propToken, avatarVersion }) => {
  // DÒNG KIỂM TRA: nếu KHÔNG thấy dòng này trong Console khi mở trang,
  // nghĩa là trình duyệt đang chạy bundle JS CŨ, chưa nhận code mới.
  console.log('%c[ProfileBanner] BUILD v4 loaded', 'color: lime; font-weight: bold;');

  const name = user?.name || "Player 1";
  const email = user?.email || "player1@gmail.com";
  const damage = user?.damage ?? user?.str ?? 1;
  const coins = user?.coins ?? 0;

  const activeTeam = user?.team || teamName || 1;
  const token = propToken || localStorage.getItem('token');
  const userId = user?.id || user?.user_id;

  const [equippedUrls, setEquippedUrls] = useState({});
  const [boss, setBoss] = useState({
    boss_id: null,
    boss_name: "Loading...",
    health: 100,
    max_health: 100,
    reward_coins: 10,
    image_url: ""
  });
  const [isHit, setIsHit] = useState(false);

  const fetchBossData = useCallback(async () => {
    if (!token || !activeTeam) return;
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    try {
      const resBoss = await fetch(`${API_BASE_URL}/get-raid-boss/${activeTeam}`, {
        headers,
        cache: 'no-store'
      });
      if (resBoss.ok) {
        const bossData = await resBoss.json();
        console.log('[fetchBossData] dữ liệu boss mới nhận từ server:', bossData);

        setBoss((prev) => {
          const isSameBoss = prev.boss_id != null && bossData.boss_id === prev.boss_id;
          const isStaleHealth = isSameBoss && bossData.health > prev.health;

          return {
            ...bossData,
            health: isStaleHealth ? prev.health : bossData.health
          };
        });
      }
    } catch (err) {
      console.error("Lỗi tải dữ liệu boss:", err);
    }
  }, [token, activeTeam]);

  const fetchAvatarData = useCallback(async () => {
    if (!token || !userId) return;
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    try {
      const resAvatar = await fetch(`${API_BASE_URL}/user/equipped-avatar/${userId}`, {
        headers,
        cache: 'no-store'
      });
      if (resAvatar.ok) {
        const avatarUrls = await resAvatar.json();
        setEquippedUrls(avatarUrls);
      }
    } catch (err) {
      console.error("Lỗi tải dữ liệu avatar:", err);
    }
  }, [token, userId]);

  useEffect(() => {
    fetchBossData();
    fetchAvatarData();
  }, [fetchBossData, fetchAvatarData, avatarVersion]);

  useEffect(() => {
    console.log('[ProfileBanner] Gắn listener raid:boss-updated');

    const handleBossUpdated = (event) => {
      const bossResult = event.detail;
      console.log('%c[raid:boss-updated] NHẬN ĐƯỢC EVENT:', 'color: orange; font-weight: bold;', bossResult);

      if (bossResult && bossResult.boss_defeated) {
        const next = bossResult.next_boss;
        if (next) {
          setBoss((prev) => ({
            ...prev,
            boss_id: next.id,
            boss_name: next.name,
            health: next.health,
            max_health: next.health,
            reward_coins: next.reward_coins
          }));
        }
        fetchBossData();
      } else if (bossResult && typeof bossResult.current_health === "number") {
        console.log('[raid:boss-updated] Cập nhật health ngay lập tức thành:', bossResult.current_health);
        setBoss((prev) => ({ ...prev, health: bossResult.current_health }));
      } else {
        console.warn('[raid:boss-updated] bossResult rỗng/không hợp lệ, fallback sang fetchBossData()');
        fetchBossData();
      }

      setIsHit(true);
      setTimeout(() => setIsHit(false), 300);
    };

    window.addEventListener('raid:boss-updated', handleBossUpdated);
    return () => {
      console.log('[ProfileBanner] Gỡ listener raid:boss-updated (component unmount hoặc deps đổi)');
      window.removeEventListener('raid:boss-updated', handleBossUpdated);
    };
  }, [fetchBossData]);

  const healthPercentage = Math.max(0, Math.min(100, (boss.health / boss.max_health) * 100));

  return (
    <div className="profile-banner">
      <div className="avatar-box" style={{ width: '150px', height: '150px', flexShrink: 0, borderRadius: '12px', overflow: 'hidden' }}>
        <AvatarDisplay equippedItems={equippedUrls} />
      </div>

      <div className="user-info">
        <h3>{name}</h3>
        <p>{email}</p>
        <div className="user-stats-text">
          <div><span style={{ marginRight: '8px' }}>⚔️</span><span>{damage} DMG</span></div>
          <div><span style={{ marginRight: '8px' }}>🪙</span><span>{coins} Coins</span></div>
        </div>
      </div>

      <div className={`boss-section ${isHit ? 'boss-hit' : ''}`}>
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
              <div className="boss-hp-fill" style={{ width: `${healthPercentage}%` }}></div>
            </div>
            <span className="boss-hp-text">{boss.health} / {boss.max_health} HP</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileBanner;