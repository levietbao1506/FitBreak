import React from 'react';
import '../style/avatarDisplay.css';

const AvatarDisplay = ({ equippedItems = {} }) => {
  const handleImageError = (layerName, src, e) => {
    console.error(`[AvatarDisplay] Lỗi tải ảnh layer '${layerName}':`, src);
    e.target.style.display = 'none';
  };

  return (
    <div className="avatar-container">
      {/* 1. Background */}
      {equippedItems.background && (
        <img
          src={equippedItems.background}
          alt="background"
          className="avatar-layer layer-bg"
          onError={(e) => handleImageError('background', equippedItems.background, e)}
        />
      )}

      {/* 2. Skin (Thân & Da) */}
      {equippedItems.skin && (
        <img
          src={equippedItems.skin}
          alt="skin"
          className="avatar-layer layer-skin"
          onError={(e) => handleImageError('skin', equippedItems.skin, e)}
        />
      )}

      {/* 3. Head (Khuôn mặt) - Nếu có */}
      {equippedItems.head && (
        <img
          src={equippedItems.head}
          alt="head"
          className="avatar-layer layer-head"
          onError={(e) => handleImageError('head', equippedItems.head, e)}
        />
      )}

      {/* 4. Shirt (Áo) */}
      {equippedItems.shirt && (
        <img
          src={equippedItems.shirt}
          alt="shirt"
          className="avatar-layer layer-shirt"
          onError={(e) => handleImageError('shirt', equippedItems.shirt, e)}
        />
      )}

      {/* 5. Hair (Tóc) */}
      {equippedItems.hair && (
        <img
          src={equippedItems.hair}
          alt="hair"
          className="avatar-layer layer-hair"
          onError={(e) => handleImageError('hair', equippedItems.hair, e)}
        />
      )}

      {/* 6. Weapon (Vũ khí) */}
      {equippedItems.weapon && (
        <img
          src={equippedItems.weapon}
          alt="weapon"
          className="avatar-layer layer-weapon"
          onError={(e) => handleImageError('weapon', equippedItems.weapon, e)}
        />
      )}
    </div>
  );
};

export default AvatarDisplay;