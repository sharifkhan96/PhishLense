import React from 'react';
import { TrafficEvent } from '../api/client';
import './TrafficEventCard.css';

interface TrafficEventCardProps {
  event: TrafficEvent;
  onClick: () => void;
}

const TrafficEventCard: React.FC<TrafficEventCardProps> = ({ event, onClick }) => {
  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'malicious': return '#ef4444';
      case 'normal': return '#22c55e';
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
    <div className="traffic-event-card" onClick={onClick}>
      <div className="event-header">
        <div className="event-classification" style={{ color: getClassificationColor(event.classification) }}>
          {event.classification.toUpperCase()}
        </div>
        {event.ml_prediction && (
          <div className="ml-badge">
            ML: {event.ml_prediction} ({event.ml_confidence ? (event.ml_confidence * 100).toFixed(0) : 0}%)
          </div>
        )}
      </div>

      <div className="event-content">
        <div className="event-info">
          <div className="info-row">
            <strong>Source IP:</strong> {event.source_ip}
          </div>
          {event.destination_ip && (
            <div className="info-row">
              <strong>Destination IP:</strong> {event.destination_ip}
            </div>
          )}
          {event.port && (
            <div className="info-row">
              <strong>Port:</strong> {event.port}
            </div>
          )}
          <div className="info-row">
            <strong>Payload Type:</strong> {event.payload_type}
          </div>
        </div>

        <div className="event-payload">
          <strong>Payload:</strong>
          <pre>{truncate(event.payload)}</pre>
        </div>
      </div>

      <div className="event-footer">
        <div className="event-meta">
          <span>{formatDate(event.date_time)}</span>
          {event.risk_score !== null && (
            <span className="risk-score">Risk: {event.risk_score.toFixed(0)}/100</span>
          )}
        </div>
        {event.sandbox_executed && (
          <div className="sandbox-indicator">🧪 Sandbox Executed</div>
        )}
      </div>
    </div>
  );
};

export default TrafficEventCard;


