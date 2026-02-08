import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { threatAPI, Threat } from '../api/client';
import ThreatCard from './ThreatCard';
import ThreatForm from './ThreatForm';
import StatsPanel from './StatsPanel';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadThreats();
    loadStats();
    const interval = setInterval(() => {
      loadThreats();
      loadStats();
    }, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadThreats = async () => {
    try {
      const response = await threatAPI.getAll();
      setThreats(response.data);
    } catch (error) {
      console.error('Error loading threats:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await threatAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleThreatSubmit = async (data: any) => {
    try {
      setShowForm(false);
      const response = await threatAPI.create(data);
      navigate(`/threat/${response.data.id}`);
    } catch (error) {
      console.error('Error creating threat:', error);
      alert('Error analyzing threat. Please try again.');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return <div className="loading">Loading threats...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Security Dashboard</h2>
        <button 
          className="btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ Analyze New Threat'}
        </button>
      </div>

      {showForm && (
        <div className="form-container">
          <ThreatForm onSubmit={handleThreatSubmit} />
        </div>
      )}

      {stats && <StatsPanel stats={stats} />}

      <div className="threats-section">
        <h3>Recent Threats</h3>
        {threats.length === 0 ? (
          <div className="empty-state">
            <p>No threats analyzed yet. Click "Analyze New Threat" to get started.</p>
          </div>
        ) : (
          <div className="threats-grid">
            {threats.map((threat) => (
              <ThreatCard
                key={threat.id}
                threat={threat}
                onClick={() => navigate(`/threat/${threat.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;


