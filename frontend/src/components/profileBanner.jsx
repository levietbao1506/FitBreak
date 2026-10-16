import { useEffect, useState, useCallback, useRef } from 'react';
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
    boss_id: null,
    boss_name: "Loading...",
    health: 100,
    max_health: 100,
    reward_coins: 10,
    image_url: ""
  });
  const [isHit, setIsHit] = useState(false);

  const requestIdRef = useRef(0);

  const fetchBossData = useCallback(async () => {
    if (!token || !activeTeam) return;
    const myRequestId = ++requestIdRef.current;

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    try {
      const resBoss = await fetch(`${API_BASE_URL}/get-raid-boss/${activeTeam}`, {
        headers,
        cache: 'no-store'
      });

      if (myRequestId !== requestIdRef.current) return;

      if (resBoss.ok) {
        const bossData = await resBoss.json();

        if (myRequestId !== requestIdRef.current) return;

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
    const handleBossUpdated = (event) => {
      const bossResult = event.detail;

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
        setBoss((prev) => ({ ...prev, health: bossResult.current_health }));
      } else {
        fetchBossData();
      }

      setIsHit(true);
      setTimeout(() => setIsHit(false), 300);
    };

    window.addEventListener('raid:boss-updated', handleBossUpdated);
    return () => {
      window.removeEventListener('raid:boss-updated', handleBossUpdated);
    };
  }, [fetchBossData]);

  const healthPercentage = Math.max(0, Math.min(100, (boss.health / boss.max_health) * 100));

  return (
    <div className="profile-banner">
      <div className="profile-banner-inner">
        <div className="user-profile-group">
          <div className="avatar-box">
            <AvatarDisplay equippedItems={equippedUrls} />
            <div className="avatar-rank-badge">LVL 1</div>
          </div>

          <div className="user-info">
            <div className="user-name-row">
              <h3>{name}</h3>
              <span className="user-team-badge">Team #{activeTeam}</span>
            </div>
            <p className="user-email-text">{email}</p>
            <div className="user-stats-text">
              <div className="stat-pill stat-damage">
                <span className="stat-icon">⚔️</span>
                <span className="stat-num">{damage}</span>
                <span className="stat-label">DMG</span>
              </div>
              <div className="stat-pill stat-coins">
                <span className="stat-icon">🪙</span>
                <span className="stat-num">{coins.toLocaleString()}</span>
                <span className="stat-label">Coins</span>
              </div>
            </div>
          </div>
        </div>

        <div className={`boss-section ${isHit ? 'boss-hit' : ''}`}>
          <div className="boss-tag-banner">
            <span className="boss-tag-dot"></span>
            <span>ACTIVE RAID BOSS</span>
          </div>

          <div className="boss-details">
            <div className="boss-header">
              <span className="boss-title">{boss.boss_name}</span>
              <span className="boss-reward">🪙 +{boss.reward_coins} Coins</span>
            </div>

            <div className="boss-hp-container">
              <div className="boss-hp-bar">
                <div className="boss-hp-fill" style={{ width: `${healthPercentage}%` }}></div>
              </div>
              <div className="boss-hp-meta">
                <span className="boss-hp-percent">{Math.round(healthPercentage)}%</span>
                <span className="boss-hp-text">{boss.health} / {boss.max_health} HP</span>
              </div>
            </div>
          </div>

          <div className="boss-avatar">
            {boss.image_url ? (
              <img src={boss.image_url} alt={boss.boss_name} />
            ) : (
              <div className="boss-placeholder">👾</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileBanner;