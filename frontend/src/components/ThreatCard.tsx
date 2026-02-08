import React from 'react';
import { Threat } from '../api/client';
import './ThreatCard.css';

interface ThreatCardProps {
  threat: Threat;
  onClick: () => void;
}

const ThreatCard: React.FC<ThreatCardProps> = ({ threat, onClick }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'analyzing': return '#3b82f6';
      case 'executing': return '#f59e0b';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncate = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="threat-card" onClick={onClick}>
      <div className="threat-card-header">
        <div className="threat-type-badge">
          {threat.threat_type.toUpperCase()}
        </div>
        {threat.severity && (
          <div
            className="severity-badge"
            style={{ backgroundColor: getSeverityColor(threat.severity) }}
          >
            {threat.severity.toUpperCase()}
          </div>
        )}
      </div>

      <div className="threat-card-content">
        <div className="threat-source">
          <strong>Source:</strong> {threat.source || 'Unknown'}
        </div>
        <div className="threat-content-preview">
          {truncate(threat.content)}
        </div>
      </div>

      <div className="threat-card-footer">
        <div className="threat-meta">
          <span
            className="status-badge"
            style={{ color: getStatusColor(threat.status) }}
          >
            {threat.status.replace('_', ' ').toUpperCase()}
          </span>
          {threat.risk_score !== null && (
            <span className="risk-score">
              Risk: {threat.risk_score.toFixed(0)}/100
            </span>
          )}
        </div>
        <div className="threat-date">
          {formatDate(threat.created_at)}
        </div>
        {threat.sandbox_executed && (
          <div className="sandbox-indicator">
            🧪 Sandbox Executed
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreatCard;


