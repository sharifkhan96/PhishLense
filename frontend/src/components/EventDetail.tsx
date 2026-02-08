import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { trafficAPI, TrafficEvent } from '../api/client';
import './EventDetail.css';

const EventDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [event, setEvent] = useState<TrafficEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [executingSandbox, setExecutingSandbox] = useState(false);

  useEffect(() => {
    if (id) {
      loadEvent();
      const interval = setInterval(() => {
        loadEvent();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [id]);

  const loadEvent = async () => {
    if (!id) return;
    try {
      const response = await trafficAPI.getById(parseInt(id));
      setEvent(response.data);
    } catch (error) {
      console.error('Error loading event:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteSandbox = async () => {
    if (!id) return;
    setExecutingSandbox(true);
    try {
      await trafficAPI.executeSandbox(parseInt(id));
      // Wait a bit then reload to get results
      setTimeout(() => {
        loadEvent();
        setExecutingSandbox(false);
      }, 2000);
    } catch (error: any) {
      console.error('Error executing sandbox:', error);
      alert(`Error executing in sandbox: ${error.response?.data?.message || error.message || 'Unknown error'}`);
      setExecutingSandbox(false);
    }
  };

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'malicious': return '#ef4444';
      case 'normal': return '#22c55e';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return <div className="loading">Loading event details...</div>;
  }

  if (!event) {
    return <div className="error">Event not found</div>;
  }

  return (
    <div className="event-detail">
      <div className="detail-header">
        <button className="btn-back" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
        {!event.sandbox_executed && (
          <button 
            className="btn-execute" 
            onClick={handleExecuteSandbox}
            disabled={executingSandbox}
          >
            {executingSandbox ? '⏳ Executing...' : '🛡️ Execute in Sandbox'}
          </button>
        )}
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h2>Event Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Classification</label>
              <div className="value" style={{ color: getClassificationColor(event.classification) }}>
                {event.classification.toUpperCase()}
              </div>
            </div>
            <div className="info-item">
              <label>Source IP</label>
              <div className="value">{event.source_ip}</div>
            </div>
            <div className="info-item">
              <label>Destination IP</label>
              <div className="value">{event.destination_ip || 'N/A'}</div>
            </div>
            <div className="info-item">
              <label>Port</label>
              <div className="value">{event.port || 'N/A'}</div>
            </div>
            <div className="info-item">
              <label>Payload Type</label>
              <div className="value">{event.payload_type}</div>
            </div>
            <div className="info-item">
              <label>Date & Time</label>
              <div className="value">{new Date(event.date_time).toLocaleString()}</div>
            </div>
            {event.ml_prediction && (
              <div className="info-item">
                <label>ML Prediction</label>
                <div className="value">
                  {event.ml_prediction} ({event.ml_confidence ? (event.ml_confidence * 100).toFixed(1) : 0}% confidence)
                </div>
              </div>
            )}
            {event.risk_score !== null && (
              <div className="info-item">
                <label>Risk Score</label>
                <div className="value risk-score">{event.risk_score.toFixed(1)}/100</div>
              </div>
            )}
          </div>
        </div>

        <div className="detail-section">
          <h2>Payload</h2>
          <div className="content-box">
            <pre>{event.payload}</pre>
          </div>
        </div>

        {event.ai_explanation && (
          <div className="detail-section">
            <h2>What Happened</h2>
            <div className="analysis-box">
              <p>{event.ai_explanation}</p>
            </div>
          </div>
        )}

        {event.actions_taken && event.actions_taken.length > 0 && (
          <div className="detail-section">
            <h2>What the App Did</h2>
            <div className="actions-box">
              <ul>
                {event.actions_taken.map((action, idx) => (
                  <li key={idx}>{action}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {event.recommendations && (
          <div className="detail-section">
            <h2>What to Do Next</h2>
            <div className="recommendations-box">
              <p>{event.recommendations}</p>
            </div>
          </div>
        )}

        {event.sandbox_executed && (
          <div className="detail-section">
            <h2>🛡️ Sandbox Execution Results</h2>
            <div className="sandbox-results">
              {event.sandbox_results ? (
                <>
                  <div className="results-status">
                    <strong>Status:</strong>{' '}
                    <span style={{ color: event.sandbox_results.success !== false ? '#22c55e' : '#ef4444' }}>
                      {event.sandbox_results.success !== false ? '✅ Success' : '❌ Failed'}
                    </span>
                  </div>

                  {event.sandbox_results.actions_taken && event.sandbox_results.actions_taken.length > 0 && (
                    <div className="results-subsection">
                      <h3>Actions Taken</h3>
                      <ul>
                        {event.sandbox_results.actions_taken.map((action: string, idx: number) => (
                          <li key={idx}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {event.sandbox_results.observations && event.sandbox_results.observations.length > 0 && (
                    <div className="results-subsection">
                      <h3>Observations</h3>
                      <ul>
                        {event.sandbox_results.observations.map((obs: string, idx: number) => (
                          <li key={idx}>{obs}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {event.sandbox_results.redirects && event.sandbox_results.redirects.length > 0 && (
                    <div className="results-subsection">
                      <h3>Redirects Followed ({event.sandbox_results.redirects.length})</h3>
                      <ol>
                        {event.sandbox_results.redirects.map((redirect: any, idx: number) => (
                          <li key={idx}>
                            <strong>{redirect.status || 'Redirect'}:</strong>{' '}
                            <span className="redirect-from">{redirect.from}</span> →{' '}
                            <span className="redirect-to">{redirect.to}</span>
                            {redirect.reason && <span className="redirect-reason"> ({redirect.reason})</span>}
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {event.sandbox_results.forms_found && event.sandbox_results.forms_found.length > 0 && (
                    <div className="results-subsection">
                      <h3>Forms Detected & Submitted ({event.sandbox_results.forms_found.length})</h3>
                      {event.sandbox_results.forms_found.map((form: any, idx: number) => (
                        <div key={idx} className="form-item">
                          <strong>Form {idx + 1}:</strong> <code>{form.method || 'GET'}</code>{' '}
                          <code>{form.action || '(no action)'}</code>
                          {form.fields && form.fields.length > 0 && (
                            <ul>
                              {form.fields.map((field: any, fIdx: number) => (
                                <li key={fIdx}>
                                  <code>{field.name || '(unnamed)'}</code> ({field.type || 'text'})
                                  {field.required && ' <strong>*required</strong>'}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {event.sandbox_results.errors && event.sandbox_results.errors.length > 0 && (
                    <div className="results-subsection error-subsection">
                      <h3>Errors</h3>
                      <ul>
                        {event.sandbox_results.errors.map((error: string, idx: number) => (
                          <li key={idx} style={{ color: '#ef4444' }}>❌ {error}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {!event.sandbox_results.actions_taken?.length &&
                    !event.sandbox_results.observations?.length &&
                    !event.sandbox_results.redirects?.length &&
                    !event.sandbox_results.forms_found?.length &&
                    !event.sandbox_results.errors?.length && (
                      <div className="results-subsection">
                        <p>No detailed results available. Sandbox execution completed.</p>
                      </div>
                    )}
                </>
              ) : (
                <div className="results-subsection">
                  <p>Sandbox execution completed, but no results data available.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EventDetail;

