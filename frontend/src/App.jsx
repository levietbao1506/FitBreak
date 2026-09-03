import React, { useState, useEffect } from 'react';
import Header from './components/header';
import ProfileBanner from './components/ProfileBanner';
import TaskBoard from './components/TaskBoard';
import LogIn from "./components/logIn";
import SignUp from "./components/signUp";
import UpdateProfile from './components/updateProfile';
import CreateProfile from "./components/createProfile";
import './App.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [activeTab, setActiveTab] = useState('tasks');
  const [user, setUser] = useState(null);
  const [showCreateProfileModal, setShowCreateProfileModal] = useState(false);

  const fetchUserProfileByEmail = async (email, token) => {
    if (!email || !token) return null;

    try {
      const response = await fetch(`http://localhost:8000/profiles/get-profile-by-email/${email}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        console.warn("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return null;
      }

      if (response.ok) {
        const profileData = await response.json();
        return profileData;
      }
      return null;
    } catch (error) {
      console.error("Lỗi khi lấy thông tin profile:", error);
      return null;
    }
  };

  useEffect(() => {
    const checkUserStatus = async () => {
      const savedUser = localStorage.getItem('user');
      const token = localStorage.getItem('token');

      if (token && savedUser) {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        setCurrentScreen('main');

        const profile = await fetchUserProfileByEmail(parsedUser.email, token);

        if (profile) {
          setUser((prev) => ({ ...prev, ...profile, hasProfile: true }));
          setShowCreateProfileModal(false);
        } else {
          setShowCreateProfileModal(true);
        }
      }
    };

    checkUserStatus();
  }, []);

  const handleAuthSuccess = async (data, isSignUp = false) => {
    const token = data?.access_token || data?.token;
    const userObj = data?.user;

    if (token) localStorage.setItem('token', token);
    if (userObj) {
      localStorage.setItem('user', JSON.stringify(userObj));
      setUser(userObj);
    }

    setCurrentScreen('main');

    if (isSignUp) {
      setShowCreateProfileModal(true);
      return;
    }

    const profile = await fetchUserProfileByEmail(userObj?.email, token);

    if (profile) {
      setUser((prev) => ({ ...prev, ...profile, hasProfile: true }));
      setShowCreateProfileModal(false);
    } else {
      setShowCreateProfileModal(true);
    }
  };

  const handleUpdateProfileSuccess = (updatedData) => {
    if (updatedData?.user) {
      setUser(updatedData.user);
      localStorage.setItem('user', JSON.stringify(updatedData.user));
    }
  };

  const handleCreateProfileSuccess = (data) => {
    const updatedUser = { ...user, ...(data?.user || {}), hasProfile: true };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    
    setShowCreateProfileModal(false);
  };

  const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  setUser(null);
  setCurrentScreen('login');
};

  if (currentScreen === 'main') {
    return (
      <div className="app-container">
        <Header 
          user={user} 
          onLogout={handleLogout} 
          activeTab={activeTab} 
          onSelectTab={setActiveTab} 
        />
        <ProfileBanner user={user} />
        
        <div className="main-content">
          {activeTab === 'tasks' && <TaskBoard user={user} />}
          {activeTab === 'profile' && (
            <UpdateProfile onUpdateProfileSuccess={handleUpdateProfileSuccess} />
          )}
        </div>
        {showCreateProfileModal && (
          <CreateProfile 
            user={user}
            onCreateProfileSuccess={handleCreateProfileSuccess}
          />
        )}
      </div>
    );
  }

  if (currentScreen === 'signup') {
    return (
      <SignUp 
        onSignUpSuccess={(data) => handleAuthSuccess(data, true)}
        onGoToLogIn={() => setCurrentScreen('login')} 
      />
    );
  }

  return (
    <LogIn 
      onLoginSuccess={handleAuthSuccess} 
      onGoToSignUp={() => setCurrentScreen('signup')} 
    />
  );
}

export default App;