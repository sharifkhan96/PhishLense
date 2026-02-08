import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import SignUp from './components/SignUp';
import TrafficDashboard from './components/TrafficDashboard';
import ThreatDetail from './components/ThreatDetail';
import EventDetail from './components/EventDetail';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" /> : <SignUp />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <TrafficDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/threat/:id"
        element={
          <ProtectedRoute>
            <ThreatDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/eventsHappened/:id"
        element={
          <ProtectedRoute>
            <EventDetail />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

