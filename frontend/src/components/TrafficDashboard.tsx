import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { trafficAPI, TrafficEvent, PaginatedResponse, mediaAPI, MediaAnalysis, PaginatedResponse as MediaPaginatedResponse } from '../api/client';
import TrafficEventCard from './TrafficEventCard';
import MediaAnalysisForm from './MediaAnalysisForm';
import MediaAnalysisCard from './MediaAnalysisCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './TrafficDashboard.css';

const TrafficDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [events, setEvents] = useState<TrafficEvent[]>([]);
  const [mediaAnalyses, setMediaAnalyses] = useState<MediaAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [filter, setFilter] = useState<string>('all');
  const [showMediaForm, setShowMediaForm] = useState(false);
  const [activeTab, setActiveTab] = useState<'traffic' | 'media'>('traffic');
  const navigate = useNavigate();

  useEffect(() => {
    loadEvents();
    loadStats();
    if (activeTab === 'media') {
      loadMediaAnalyses();
    }
    const interval = setInterval(() => {
      loadEvents();
      loadStats();
      if (activeTab === 'media') {
        loadMediaAnalyses();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [filter, activeTab]);

  const loadEvents = async () => {
    try {
      const classification = filter !== 'all' ? filter : undefined;
      const response = await trafficAPI.getAll(classification);
      // Handle paginated response (Django REST Framework returns {results: [], ...})
      const paginatedData = response.data as PaginatedResponse<TrafficEvent>;
      setEvents(paginatedData.results || []);
    } catch (error) {
      console.error('Error loading events:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await trafficAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadMediaAnalyses = async () => {
    try {
      const response = await mediaAPI.getAll();
      const paginatedData = response.data as MediaPaginatedResponse<MediaAnalysis>;
      setMediaAnalyses(paginatedData.results || []);
    } catch (error) {
      console.error('Error loading media analyses:', error);
      setMediaAnalyses([]);
    }
  };

  const handleMediaAnalysisComplete = (analysis: MediaAnalysis) => {
    setShowMediaForm(false);
    loadMediaAnalyses();
    // Optionally navigate to analysis detail or show notification
  };

  if (loading && !stats) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="traffic-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="dashboard-title">
            <img src="/logo.jpg" alt="PhishLense Logo" className="logo-small" />
            <h1>PhishLense Dashboard</h1>
          </div>
          <div className="header-actions">
            <span className="user-info">Welcome, {user?.username}</span>
            <button onClick={logout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </header>

      {stats && activeTab === 'traffic' && (
        <>
          <div className="stats-section">
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
          
          <div className="charts-section">
            <div className="chart-container">
              <h3>Traffic Classification</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={[
                    { name: 'All', value: stats.total },
                    { name: 'Normal', value: stats.normal },
                    { name: 'Malicious', value: stats.malicious },
                    { name: 'Unknown', value: stats.unknown || 0 }
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="chart-container">
              <h3>Traffic Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Normal', value: stats.normal, color: '#4CAF50' },
                      { name: 'Malicious', value: stats.malicious, color: '#f44336' },
                      { name: 'Unknown', value: stats.unknown || 0, color: '#9E9E9E' }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[
                      { name: 'Normal', value: stats.normal, color: '#4CAF50' },
                      { name: 'Malicious', value: stats.malicious, color: '#f44336' },
                      { name: 'Unknown', value: stats.unknown || 0, color: '#9E9E9E' }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      <div className="dashboard-tabs">
        <button
          className={activeTab === 'traffic' ? 'active' : ''}
          onClick={() => setActiveTab('traffic')}
        >
          Traffic Events
        </button>
        <button
          className={activeTab === 'media' ? 'active' : ''}
          onClick={() => setActiveTab('media')}
        >
          Media Analysis
        </button>
      </div>

      {activeTab === 'media' && (
        <div className="media-section">
          <div className="section-header">
            <h2>AI Media Analysis</h2>
            <button
              className="btn-primary"
              onClick={() => setShowMediaForm(!showMediaForm)}
            >
              {showMediaForm ? 'Cancel' : '+ Analyze Media'}
            </button>
          </div>
          {showMediaForm && (
            <MediaAnalysisForm onAnalysisComplete={handleMediaAnalysisComplete} />
          )}
          <div className="media-analyses-list">
            {mediaAnalyses.length === 0 ? (
              <div className="empty-state">
                <p>No media analyses yet. Click "Analyze Media" to get started.</p>
              </div>
            ) : (
              mediaAnalyses.map((analysis) => (
                <MediaAnalysisCard
                  key={analysis.id}
                  analysis={analysis}
                  onClick={() => {}}
                />
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'traffic' && (
        <div className="dashboard-content">
          <div className="content-header">
            <h2>Recent Events</h2>
            <div className="filter-buttons">
              <button
                className={filter === 'all' ? 'active' : ''}
                onClick={() => setFilter('all')}
              >
                All
              </button>
              <button
                className={filter === 'normal' ? 'active' : ''}
                onClick={() => setFilter('normal')}
              >
                Normal
              </button>
              <button
                className={filter === 'malicious' ? 'active' : ''}
                onClick={() => setFilter('malicious')}
              >
                Malicious
              </button>
            </div>
          </div>

          {!Array.isArray(events) || events.length === 0 ? (
            <div className="empty-state">
              <p>No traffic events yet. Events will appear here when traffic is received.</p>
            </div>
          ) : (
            <div className="events-list">
              {events.map((event) => (
                <TrafficEventCard
                  key={event.id}
                  event={event}
                  onClick={() => navigate(`/eventsHappened/${event.id}`)}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TrafficDashboard;

