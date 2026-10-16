import { useState, useEffect, useCallback } from 'react';
import AvatarDisplay from './avatarDisplay';
import '../style/shop.css';

const API_BASE_URL = 'http://localhost:8000';

const CATEGORIES = [
  { id: 'all', label: 'Tất cả' },
  { id: 'shirt', label: '👕 Áo' },
  { id: 'hair', label: '💇 Tóc' },
  { id: 'skin', label: '🎨 Da' },
  { id: 'background', label: '🖼️ Phông nền' },
  { id: 'weapon', label: '⚔️ Vũ khí' },
];

const Shop = ({ user, onUpdateCoins, onAvatarUpdated, onStatsUpdated }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');

  const [equippedUrls, setEquippedUrls] = useState({
    background: null,
    skin: null,
    shirt: null,
    hair: null,
    weapon: null
  });

  const currentUserId = user?.id || user?.user_id;

  const getItemCategory = (name = '') => {
    const lower = name.toLowerCase();
    if (lower.includes('shirt')) return 'shirt';
    if (lower.includes('hair')) return 'hair';
    if (lower.includes('skin')) return 'skin';
    if (lower.includes('background')) return 'background';
    return 'weapon';
  };

  const fetchShopAndAvatarData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Không tìm thấy token, vui lòng đăng nhập lại.');
        setLoading(false);
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const url = currentUserId ? `${API_BASE_URL}/items?user_id=${currentUserId}` : `${API_BASE_URL}/items`;
      const resItems = await fetch(url, { headers });
      const rawText = await resItems.text();

      if (!resItems.ok) {
        setError('Lỗi tải vật phẩm: ' + rawText);
        setItems([]);
      } else {
        const data = JSON.parse(rawText);
        setItems(Array.isArray(data) ? data : []);
      }

      if (currentUserId) {
        const resAvatar = await fetch(`${API_BASE_URL}/user/equipped-avatar/${currentUserId}`, { headers });
        if (resAvatar.ok) {
          const avatarData = await resAvatar.json();
          setEquippedUrls(avatarData);
        }
      }
    } catch (err) {
      console.error('Lỗi tải dữ liệu Cửa hàng:', err);
      setError('Lỗi kết nối: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [currentUserId]);

  useEffect(() => {
    fetchShopAndAvatarData();
  }, [fetchShopAndAvatarData]);

  const handlePurchase = async (item) => {
    if ((user?.coins || 0) < item.price) {
      setMessage('Bạn không đủ Coins!');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE_URL}/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: String(currentUserId),
          item_id: item.item_id
        })
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        setMessage(data.detail || data.message || 'Mua hàng thất bại');
        return;
      }

      setMessage(`Đã mua và trang bị: ${item.name}!`);
      if (onUpdateCoins) onUpdateCoins(data.remaining_coin);

      await fetchShopAndAvatarData();
      if (onAvatarUpdated) onAvatarUpdated();
      if (onStatsUpdated) await onStatsUpdated(); 
    } catch (err) {
      console.error('Lỗi mua hàng:', err);
      setMessage('Có lỗi xảy ra khi mua hàng!');
    }
  };

  const handleEquip = async (item) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE_URL}/equip`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: currentUserId,
          item_id: item.item_id
        })
      });

      if (!res.ok) {
        setMessage('Trang bị thất bại!');
        return;
      }

      setMessage(`Đã trang bị thành công: ${item.name}!`);
      await fetchShopAndAvatarData();
      if (onAvatarUpdated) onAvatarUpdated();
      if (onStatsUpdated) await onStatsUpdated();
    } catch (err) {
      console.error('Lỗi trang bị:', err);
      setMessage('Có lỗi xảy ra khi trang bị!');
    }
  };

  const filteredItems = activeCategory === 'all'
    ? items
    : items.filter((item) => getItemCategory(item.name) === activeCategory);

  return (
    <div className="shop-container">
      <div className="shop-preview-section">
        <div className="shop-preview-header">
          <span className="shop-preview-badge">HERO PREVIEW</span>
          <h3>Xem trước Nhân vật</h3>
        </div>
        
        <div className="avatar-preview-box">
          <AvatarDisplay equippedItems={equippedUrls} />
        </div>

        <div className="shop-preview-stats">
          <div className="preview-stat-item">
            <span>Ví vàng:</span>
            <span className="preview-stat-gold">🪙 {(user?.coins || 0).toLocaleString()}</span>
          </div>
          <div className="preview-stat-item">
            <span>Sức mạnh:</span>
            <span className="preview-stat-str">⚔️ {user?.damage || user?.str || 1} DMG</span>
          </div>
        </div>

        {message && <div className="shop-message">{message}</div>}
      </div>

      <div className="shop-items-section">
        <div className="shop-section-header">
          <div className="shop-title-group">
            <h2>Cửa Hàng Trang Bị</h2>
            <p>Trang bị cho anh hùng để gia tăng sức tấn công khi đánh Boss!</p>
          </div>
        </div>

        <div className="category-tabs">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              className={`tab-btn ${activeCategory === cat.id ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {error && (
          <div className="shop-error-box">{error}</div>
        )}

        {loading ? (
          <div className="shop-loading-box">
            <div className="shop-spinner"></div>
            <span>Đang tải kho trang bị...</span>
          </div>
        ) : filteredItems.length === 0 ? (
          !error && <p className="empty-category-msg">Không có vật phẩm nào trong danh mục này.</p>
        ) : (
          <div className="items-grid">
            {filteredItems.map((item) => (
              <div key={item.item_id} className={`item-card ${item.is_equipped ? 'item-equipped-card' : ''}`}>
                <div className="item-image-wrapper">
                  <div className="item-image">
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="item-image-placeholder">?</div>
                    )}
                  </div>
                  {item.is_equipped && <span className="item-active-ribbon">ĐANG DÙNG</span>}
                </div>

                <div className="item-info">
                  <h4>{item.name}</h4>
                  <div className="item-stats-row">
                    <span className="item-stat">+{item.strength} DMG</span>
                    <span className="item-price">🪙 {item.price}</span>
                  </div>
                </div>

                <div className="item-actions">
                  {item.is_equipped ? (
                    <button className="btn-equipped" disabled>
                      ✓ Đang dùng
                    </button>
                  ) : item.is_owned ? (
                    <button className="btn-equip" onClick={() => handleEquip(item)}>
                      Trang bị
                    </button>
                  ) : (
                    <button className="btn-buy" onClick={() => handlePurchase(item)}>
                      Mua ngay
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Shop;