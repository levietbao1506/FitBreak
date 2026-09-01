import React, { useState } from 'react';
import "../style/profileInformation.css"

const profileInformation = (onUpdateProfileSuccess) => {
    const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    height: '',
    weight: '',
    goal: '',
    activityFrequency: '',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Thông tin đã nhập:', formData);
    try {
      const response = await fetch('http://localhost:8000/profiles/update-profile', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(data.detail[0].msg || 'Dữ liệu nhập vào không hợp lệ!');
        }
        throw new Error(data.detail || data.message || 'Cập nhật thông tin thất bại!');
      }

      onUpdateProfileSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-form-container">
      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-content">  
          <div className="form-column">
            <div className="form-group">
              <label>Name :</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label>Age :</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label>Gender :</label>
              <input
                type="text"
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label>Height :</label>
              <input
                type="text"
                name="height"
                value={formData.height}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label>Weight :</label>
              <input
                type="text"
                name="weight"
                value={formData.weight}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="form-column">
            <div className="form-group">
              <label>Goal :</label>
              <input
                type="text"
                name="goal"
                value={formData.goal}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label>Activity Frequency :</label>
              <input
                type="text"
                name="activityFrequency"
                value={formData.activityFrequency}
                onChange={handleInputChange}
              />
            </div>
          </div>
        </div>
        
        <button type="submit" className="save-button">Lưu thông tin</button>
      </form>
    </div>
  );
};

export default profileInformation;