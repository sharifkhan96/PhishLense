import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { threatAPI, Threat } from '../api/client';
import './ThreatDetail.css';

const ThreatDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [threat, setThreat] = useState<Threat | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    if (id) {
      loadThreat();
      const interval = setInterval(() => {
        loadThreat();
      }, 3000); // Refresh every 3 seconds
      return () => clearInterval(interval);
    }
  }, [id]);

  const loadThreat = async () => {
    if (!id) return;
    try {
      const response = await threatAPI.getById(parseInt(id));
      setThreat(response.data);
    } catch (error) {
      console.error('Error loading threat:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!id) return;
    setExecuting(true);
    try {
      await threatAPI.execute(parseInt(id));
      await loadThreat();
    } catch (error) {
      console.error('Error executing threat:', error);
      alert('Error executing threat in sandbox');
    } finally {
      setExecuting(false);
    }
  };

  const handleReanalyze = async () => {
    if (!id) return;
    try {
      await threatAPI.reanalyze(parseInt(id));
      await loadThreat();
    } catch (error) {
      console.error('Error reanalyzing threat:', error);
      alert('Error reanalyzing threat');
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
    return <div className="loading">Loading threat details...</div>;
  }

  if (!threat) {
    return <div className="error">Threat not found</div>;
  }

  return (
    <div className="threat-detail">
      <div className="detail-header">
        <button className="btn-back" onClick={() => navigate('/')}>
          ← Back to Dashboard
        </button>
        <div className="header-actions">
          {!threat.sandbox_executed && threat.threat_type !== 'text' && (
            <button
              className="btn-execute"
              onClick={handleExecute}
              disabled={executing}
            >
              {executing ? 'Executing...' : 'Execute in Sandbox'}
            </button>
          )}
          <button className="btn-reanalyze" onClick={handleReanalyze}>
            Re-analyze
          </button>
        </div>
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h2>Threat Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Type</label>
              <div className="value">{threat.threat_type.toUpperCase()}</div>
            </div>
            <div className="info-item">
              <label>Source</label>
              <div className="value">{threat.source || 'Unknown'}</div>
            </div>
            <div className="info-item">
              <label>Status</label>
              <div className="value">{threat.status.replace('_', ' ').toUpperCase()}</div>
            </div>
            {threat.severity && (
              <div className="info-item">
                <label>Severity</label>
                <div
                  className="value severity-badge"
                  style={{ color: getSeverityColor(threat.severity) }}
                >
                  {threat.severity.toUpperCase()}
                </div>
              </div>
            )}
            {threat.risk_score !== null && (
              <div className="info-item">
                <label>Risk Score</label>
                <div className="value risk-score">
                  {threat.risk_score.toFixed(1)}/100
                </div>
              </div>
            )}
            <div className="info-item">
              <label>Created At</label>
              <div className="value">
                {new Date(threat.created_at).toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h2>Content</h2>
          <div className="content-box">
            <pre>{threat.content}</pre>
          </div>
        </div>

        {threat.ai_explanation && (
          <div className="detail-section">
            <h2>AI Analysis</h2>
            <div className="analysis-box">
              <p>{threat.ai_explanation}</p>
            </div>
          </div>
        )}

        {threat.recommendations && (
          <div className="detail-section">
            <h2>Recommendations</h2>
            <div className="recommendations-box">
              <p>{threat.recommendations}</p>
            </div>
          </div>
        )}

        {threat.sandbox_executed && threat.sandbox_results && (
          <div className="detail-section">
            <h2>Sandbox Execution Results</h2>
            <div className="sandbox-results">
              <div className="results-summary">
                <div className="summary-item">
                  <strong>Actions Taken:</strong> {threat.actions_taken?.length || 0}
                </div>
                {threat.sandbox_results.redirects && (
                  <div className="summary-item">
                    <strong>Redirects Followed:</strong> {threat.sandbox_results.redirects.length}
                  </div>
                )}
                {threat.sandbox_results.forms_found && (
                  <div className="summary-item">
                    <strong>Forms Found:</strong> {threat.sandbox_results.forms_found.length}
                  </div>
                )}
              </div>

              {threat.observations && (
                <div className="observations-box">
                  <h3>Observations</h3>
                  <ul>
                    {threat.observations.split('\n').map((obs, idx) => (
                      obs.trim() && <li key={idx}>{obs}</li>
                    ))}
                  </ul>
                </div>
              )}

              {threat.sandbox_results.redirects && threat.sandbox_results.redirects.length > 0 && (
                <div className="redirects-box">
                  <h3>Redirect Chain</h3>
                  <ol>
                    {threat.sandbox_results.redirects.map((redirect: any, idx: number) => (
                      <li key={idx}>
                        <strong>{redirect.status}:</strong> {redirect.from} → {redirect.to}
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {threat.sandbox_results.forms_found && threat.sandbox_results.forms_found.length > 0 && (
                <div className="forms-box">
                  <h3>Forms Detected</h3>
                  {threat.sandbox_results.forms_found.map((form: any, idx: number) => (
                    <div key={idx} className="form-item">
                      <strong>Form {idx + 1}:</strong> {form.method} {form.action || '(no action)'}
                      <ul>
                        {form.fields.map((field: any, fIdx: number) => (
                          <li key={fIdx}>
                            {field.name || '(unnamed)'} ({field.type})
                            {field.required && ' *'}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {threat.timeline_events && threat.timeline_events.length > 0 && (
          <div className="detail-section">
            <h2>Timeline</h2>
            <div className="timeline">
              {threat.timeline_events.map((event) => (
                <div key={event.id} className="timeline-event">
                  <div className="timeline-time">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-type">{event.event_type.replace('_', ' ').toUpperCase()}</div>
                    <div className="timeline-description">{event.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ThreatDetail;


