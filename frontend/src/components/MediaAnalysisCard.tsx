import React from 'react';
import { MediaAnalysis } from '../api/client';
import './MediaAnalysisCard.css';

interface MediaAnalysisCardProps {
  analysis: MediaAnalysis;
  onClick: () => void;
}

const MediaAnalysisCard: React.FC<MediaAnalysisCardProps> = ({ analysis, onClick }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'analyzing': return '#3b82f6';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getRiskColor = (score: number | null) => {
    if (!score) return '#6b7280';
    if (score >= 70) return '#ef4444';
    if (score >= 40) return '#f59e0b';
    return '#22c55e';
  };

  return (
    <div className="media-analysis-card" onClick={onClick}>
      <div className="card-header">
        <div className="media-type-badge">
          {analysis.media_type.toUpperCase()}
        </div>
        <div
          className="status-badge"
          style={{ color: getStatusColor(analysis.status) }}
        >
          {analysis.status.toUpperCase()}
        </div>
        {analysis.is_threat && (
          <div className="threat-badge">⚠️ THREAT</div>
        )}
      </div>

      {analysis.what_received && (
        <div className="feedback-section">
          <div className="feedback-item">
            <strong>📥 Received:</strong> {analysis.what_received}
          </div>
        </div>
      )}

      {analysis.what_did && (
        <div className="feedback-section">
          <div className="feedback-item">
            <strong>⚙️ Did:</strong> {analysis.what_did}
          </div>
        </div>
      )}

      {analysis.what_to_do_next && (
        <div className="feedback-section">
          <div className="feedback-item">
            <strong>➡️ Next:</strong> {analysis.what_to_do_next}
          </div>
        </div>
      )}

      {analysis.ai_analysis && (
        <div className="feedback-section">
          <details className="analysis-details">
            <summary className="analysis-summary">
              <strong>📋 Full AI Analysis</strong>
            </summary>
            <div className="analysis-content">
              {analysis.ai_analysis.split('\n').map((line, idx) => (
                <p key={idx} style={{ margin: '0.5rem 0' }}>
                  {line || '\u00A0'}
                </p>
              ))}
            </div>
          </details>
        </div>
      )}

      <div className="card-footer">
        <div className="card-meta">
          {analysis.risk_score !== null && (
            <span
              className="risk-score"
              style={{ color: getRiskColor(analysis.risk_score) }}
            >
              Risk: {analysis.risk_score.toFixed(0)}/100
            </span>
          )}
          <span className="timestamp">
            {new Date(analysis.created_at).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default MediaAnalysisCard;

