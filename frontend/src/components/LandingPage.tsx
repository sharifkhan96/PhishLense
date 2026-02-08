import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { trafficAPI } from '../api/client';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    // Try to get public stats (if available) or show demo data
    if (isAuthenticated) {
      trafficAPI.getStats()
        .then((response) => setStats(response.data))
        .catch(() => {
          // Use demo data if API fails
          setStats({
            total: 72,
            normal: 41,
            malicious: 31,
          });
        });
    } else {
      // Demo data for non-authenticated users
      setStats({
        total: 72,
        normal: 41,
        malicious: 31,
      });
    }
  }, [isAuthenticated]);

  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="nav-brand">
          <img src="/logo.jpg" alt="PhishLense Logo" className="logo" />
          <h1>PhishLense</h1>
        </div>
        <div className="nav-links">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <button onClick={() => navigate('/dashboard')} className="btn-primary">
                Go to Dashboard
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/signup" className="btn-primary">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <h1>AI Security Copilot</h1>
          <p className="hero-subtitle">
            Protect your organization with AI-powered threat analysis and automated sandbox execution
          </p>
          <div className="hero-actions">
            {!isAuthenticated && (
              <>
                <Link to="/signup" className="btn-hero-primary">
                  Get Started
                </Link>
                <Link to="/login" className="btn-hero-secondary">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2>Key Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI-Powered Analysis</h3>
              <p>Uses OpenAI GPT-4 and ML models to analyze threats and provide clear explanations</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🧪</div>
              <h3>Sandbox Execution</h3>
              <p>Safely executes suspicious content in isolated environments to observe behavior</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Real-time Dashboard</h3>
              <p>Monitor threats, view statistics, and track security events in real-time</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Traffic Analysis</h3>
              <p>Automatically receives and analyzes incoming traffic from various sources</p>
            </div>
          </div>
        </div>
      </section>

      {stats && (
        <section className="dashboard-preview">
          <div className="container">
            <h2>Dashboard Preview</h2>
            <div className="preview-stats">
              <div className="stat-card">
                <div className="stat-value">{stats.total}</div>
                <div className="stat-label">All Traffic</div>
              </div>
              <div className="stat-card normal">
                <div className="stat-value">{stats.normal}</div>
                <div className="stat-label">Normal Traffic</div>
              </div>
              <div className="stat-card malicious">
                <div className="stat-value">{stats.malicious}</div>
                <div className="stat-label">Malicious Traffic</div>
              </div>
            </div>
            {isAuthenticated && (
              <Link to="/dashboard" className="btn-view-dashboard">
                View Full Dashboard →
              </Link>
            )}
          </div>
        </section>
      )}

      <footer className="landing-footer">
        <p>© 2024 PhishLense - AI Security Copilot</p>
      </footer>
    </div>
  );
};

export default LandingPage;

