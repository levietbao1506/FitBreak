import React, { useState, useEffect } from 'react';
import Header from './components/header';
import ProfileBanner from './components/ProfileBanner';
import TaskBoard from './components/TaskBoard';
import LogIn from "./components/logIn";
import SignUp from "./components/signUp";
import './App.css';
import "./style/logIn.css";
import "./style/signUp.css";

function App() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');

    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      setCurrentScreen('main');
    }
  }, []);

  const handleAuthSuccess = (data) => {
    if (data?.access_token || data?.token) {
      localStorage.setItem('token', data.access_token || data.token);
    }
    if (data?.user) {
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
    }
    setCurrentScreen('main');
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
        <Header user={user} onLogout={handleLogout} />
        <ProfileBanner user={user} />
        <div className="main-content">
          <TaskBoard user={user} />
        </div>
      </div>
    );
  }

  if (currentScreen === 'signup') {
    return (
      <SignUp 
        onSignUpSuccess={handleAuthSuccess} 
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