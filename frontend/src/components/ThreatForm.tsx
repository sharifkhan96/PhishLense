import React, { useState } from 'react';
import { ThreatAnalysisRequest } from '../api/client';
import './ThreatForm.css';

interface ThreatFormProps {
  onSubmit: (data: ThreatAnalysisRequest) => void;
}

const ThreatForm: React.FC<ThreatFormProps> = ({ onSubmit }) => {
  const [threatType, setThreatType] = useState<'email' | 'url' | 'text' | 'link'>('url');
  const [content, setContent] = useState('');
  const [source, setSource] = useState('');
  const [executeInSandbox, setExecuteInSandbox] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      alert('Please enter threat content');
      return;
    }

    setSubmitting(true);
    onSubmit({
      threat_type: threatType,
      content: content.trim(),
      source: source.trim() || undefined,
      execute_in_sandbox: executeInSandbox,
    });
    setSubmitting(false);
  };

  return (
    <form className="threat-form" onSubmit={handleSubmit}>
      <h3>Analyze New Threat</h3>
      
      <div className="form-group">
        <label>Threat Type</label>
        <select
          value={threatType}
          onChange={(e) => setThreatType(e.target.value as any)}
          className="form-control"
        >
          <option value="url">URL</option>
          <option value="link">Link</option>
          <option value="email">Email</option>
          <option value="text">Text</option>
        </select>
      </div>

      <div className="form-group">
        <label>Source (optional)</label>
        <input
          type="text"
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="e.g., sender@example.com, suspicious-domain.com"
          className="form-control"
        />
      </div>

      <div className="form-group">
        <label>Content *</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={
            threatType === 'url' || threatType === 'link'
              ? 'Enter the suspicious URL...'
              : threatType === 'email'
              ? 'Paste the suspicious email content...'
              : 'Enter the suspicious text...'
          }
          className="form-control"
          rows={6}
          required
        />
      </div>

      <div className="form-group checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={executeInSandbox}
            onChange={(e) => setExecuteInSandbox(e.target.checked)}
          />
          Execute in sandbox (recommended)
        </label>
      </div>

      <button
        type="submit"
        className="btn-submit"
        disabled={submitting || !content.trim()}
      >
        {submitting ? 'Analyzing...' : 'Analyze Threat'}
      </button>
    </form>
  );
};

export default ThreatForm;


