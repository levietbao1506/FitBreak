import React, { useState, useEffect, useCallback } from 'react';
import AvatarDisplay from './avatarDisplay';
import '../style/shop.css';

const API_BASE_URL = 'http://localhost:8000';

// Các danh mục phân loại
const CATEGORIES = [
  { id: 'all', label: 'Tất cả' },
  { id: 'shirt', label: '👕 Áo' },
  { id: 'hair', label: '💇 Tóc' },
  { id: 'skin', label: '🎨 Da' },
  { id: 'background', label: '🖼️ Background' },
  { id: 'weapon', label: '⚔️ Vũ khí' },
];

const Shop = ({ user, onUpdateCoins, onAvatarUpdated }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  
  // State quản lý Tab danh mục đang chọn
  const [activeCategory, setActiveCategory] = useState('all');

  const [equippedUrls, setEquippedUrls] = useState({
    background: null,
    skin: null,
    shirt: null,
    hair: null,
    weapon: null
  });

  const currentUserId = user?.id || user?.user_id;

  // Hàm tự động xác định danh mục dựa vào tên vật phẩm
  const getItemCategory = (name = '') => {
    const lower = name.toLowerCase();
    if (lower.includes('shirt')) return 'shirt';
    if (lower.includes('hair')) return 'hair';
    if (lower.includes('skin')) return 'skin';
    if (lower.includes('background')) return 'background';
    return 'weapon'; // Sword, Scythe, Staff, ...
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

      // 1. Tải danh sách vật phẩm
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

      // 2. Tải URL avatar đang mặc
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

  // Mua hàng -> Tự động sở hữu & mặc đồ
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
    } catch (err) {
      console.error('Lỗi mua hàng:', err);
      setMessage('Có lỗi xảy ra khi mua hàng!');
    }
  };

  // Trang bị món ĐÃ MUA
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
    } catch (err) {
      console.error('Lỗi trang bị:', err);
      setMessage('Có lỗi xảy ra khi trang bị!');
    }
  };

  // Lọc vật phẩm theo Tab đang được chọn
  const filteredItems = activeCategory === 'all'
    ? items
    : items.filter((item) => getItemCategory(item.name) === activeCategory);

  return (
    <div className="shop-container">
      {/* Khung Xem trước Nhân vật */}
      <div className="shop-preview-section">
        <h3>Xem trước Nhân vật</h3>
        <div className="avatar-preview-box">
          <AvatarDisplay equippedItems={equippedUrls} />
        </div>
        {message && <p className="shop-message">{message}</p>}
      </div>

      {/* Cửa hàng */}
      <div className="shop-items-section">
        <h2>Cửa Hàng Vật Phẩm</h2>

        {/* Thanh Tab lọc danh mục */}
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
          <p style={{ color: '#ff6b6b', whiteSpace: 'pre-wrap' }}>{error}</p>
        )}

        {loading ? (
          <p>Đang tải cửa hàng...</p>
        ) : filteredItems.length === 0 ? (
          !error && <p className="empty-category-msg">Không có vật phẩm nào trong danh mục này.</p>
        ) : (
          <div className="items-grid">
            {filteredItems.map((item) => (
              <div key={item.item_id} className="item-card">
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

                <div className="item-info">
                  <h4>{item.name}</h4>
                  <p className="item-stat">+{item.strength} DMG</p>
                  <p className="item-price">{item.price} Coins</p>
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
                      Mua
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