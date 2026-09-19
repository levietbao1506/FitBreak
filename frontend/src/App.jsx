import React, { useState, useEffect } from 'react';
import Header from './components/header';
import ProfileBanner from './components/profileBanner';
import LogIn from "./components/logIn";
import SignUp from "./components/signUp";
import UpdateProfile from './components/updateProfile';
import CreateProfile from "./components/createProfile";
import FoodSuggest from "./components/foodSuggest";
import TimeSelector from "./components/timeSelector";
import JoinTeam from "./components/joinTeam";
import TaskBoard from "./components/taskBoard";
import Shop from './components/shop';
import './App.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [activeTab, setActiveTab] = useState('tasks');
  const [user, setUser] = useState(null);
  const [showCreateProfileModal, setShowCreateProfileModal] = useState(false);
  const [workoutSchedule, setWorkoutSchedule] = useState(null);

  // State để thông báo cập nhật Avatar toàn ứng dụng
  const [avatarVersion, setAvatarVersion] = useState(0);

  const handleAvatarUpdated = () => {
    setAvatarVersion((prev) => prev + 1);
  };
  const getScheduleKey = (u) => (u?.email ? `workoutSchedule_${u.email}` : null);

  const loadScheduleForUser = (u) => {
    const key = getScheduleKey(u);
    if (!key) return null;
    try {
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      console.error("Lỗi parse lịch tập:", e);
      return null;
    }
  };

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
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return null;
      }

      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error("Lỗi khi lấy thông tin profile:", error);
      return null;
    }
  };

  const fetchUserStats = async (token) => {
    if (!token) return null;
    try {
      const response = await fetch(`http://localhost:8000/get-stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error("Lỗi khi lấy thông tin stats:", error);
      return null;
    }
  };

  useEffect(() => {
    const checkUserStatus = async () => {
      // Xóa key cũ dùng chung cho mọi tài khoản (chỉ là dữ liệu rác)
      localStorage.removeItem('workoutSchedule');

      const savedUser = localStorage.getItem('user');
      const token = localStorage.getItem('token');

      if (token && savedUser) {
        const parsedUser = JSON.parse(savedUser);

        // Chỉ load lịch của đúng user này
        setWorkoutSchedule(loadScheduleForUser(parsedUser));

        const [profile, stats] = await Promise.all([
          fetchUserProfileByEmail(parsedUser.email, token),
          fetchUserStats(token)
        ]);

        const fullUserData = { ...parsedUser, ...profile, ...stats, hasProfile: !!profile };

        setUser(fullUserData);
        localStorage.setItem('user', JSON.stringify(fullUserData));
        setCurrentScreen('main');

        if (!profile) setShowCreateProfileModal(true);
      }
    };

    checkUserStatus();
  }, []);

  const handleAuthSuccess = async (data, isSignUp = false) => {
    const token = data?.access_token || data?.token;
    const userObj = data?.user;

    if (token) localStorage.setItem('token', token);

    setWorkoutSchedule(isSignUp ? null : loadScheduleForUser(userObj));

    setCurrentScreen('main');

    if (isSignUp) {
      if (userObj) setUser(userObj);
      setShowCreateProfileModal(true);
      return;
    }

    const [profile, stats] = await Promise.all([
      fetchUserProfileByEmail(userObj?.email, token),
      fetchUserStats(token)
    ]);

    const fullUserData = {
      ...userObj,
      ...profile,
      ...stats,
      hasProfile: !!profile
    };

    setUser(fullUserData);
    localStorage.setItem('user', JSON.stringify(fullUserData));

    if (!profile) {
      setShowCreateProfileModal(true);
    } else {
      setShowCreateProfileModal(false);
    }
  };

  const handleUpdateProfileSuccess = (updatedData) => {
    setUser((prevUser) => {
      const newProfileInfo = updatedData?.user || updatedData;
      const newUserState = { ...prevUser, ...newProfileInfo };
      localStorage.setItem('user', JSON.stringify(newUserState));
      return newUserState;
    });
  };

  const handleCreateProfileSuccess = (data) => {
    const updatedUser = { ...user, ...(data?.user || {}), hasProfile: true };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setShowCreateProfileModal(false);
  };

  const handleUpdateCoins = (newCoins) => {
    setUser((prevUser) => {
      const updatedUser = { ...prevUser, coins: newCoins };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    });
  };

  const handleRefreshStats = async () => {
    const token = localStorage.getItem('token');
    const stats = await fetchUserStats(token);
    if (!stats) return;

    setUser((prevUser) => {
      const updatedUser = { ...prevUser, ...stats };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    });
  };

  const handleUpdateSchedule = (newSchedule) => {
    setWorkoutSchedule(newSchedule);
    const key = getScheduleKey(user);
    if (key) localStorage.setItem(key, JSON.stringify(newSchedule));
  };

  const handleScheduleGenerated = (newSchedule) => {
    setWorkoutSchedule(newSchedule);
    const key = getScheduleKey(user);
    if (key) localStorage.setItem(key, JSON.stringify(newSchedule));
    setActiveTab('tasks');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setWorkoutSchedule(null);
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
        <ProfileBanner 
          user={user} 
          teamName={user?.team || 1}
          token={localStorage.getItem('token')}
          avatarVersion={avatarVersion}
        />
        
        <div className="main-content">
          {activeTab === 'tasks' && (
            <TaskBoard 
              user={user} 
              scheduleData={workoutSchedule} 
              onUpdateCoins={handleUpdateCoins}
              onUpdateSchedule={handleUpdateSchedule}
            />
          )}
          {activeTab === 'profile' && (
            <UpdateProfile onUpdateProfileSuccess={handleUpdateProfileSuccess} />
          )}
          {activeTab === 'food' && <FoodSuggest />}
          {activeTab === 'schedule' && (
            <TimeSelector onScheduleGenerated={handleScheduleGenerated} />
          )}
          {activeTab === 'team' && <JoinTeam />}
          {activeTab === 'shop' && (
            <Shop 
              user={user} 
              onUpdateCoins={handleUpdateCoins} 
              onAvatarUpdated={handleAvatarUpdated}
              onStatsUpdated={handleRefreshStats}
            />
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