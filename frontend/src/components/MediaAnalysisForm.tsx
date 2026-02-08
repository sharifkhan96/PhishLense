import React, { useState } from 'react';
import { mediaAPI, MediaAnalysis } from '../api/client';
import './MediaAnalysisForm.css';

interface MediaAnalysisFormProps {
  onAnalysisComplete: (analysis: MediaAnalysis) => void;
}

const MediaAnalysisForm: React.FC<MediaAnalysisFormProps> = ({ onAnalysisComplete }) => {
  const [mediaType, setMediaType] = useState<'text' | 'image' | 'video' | 'audio'>('text');
  const [textContent, setTextContent] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState('');
  const [organization, setOrganization] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [rateLimitStatus, setRateLimitStatus] = useState<any>(null);

  React.useEffect(() => {
    loadRateLimitStatus();
  }, []);

  const loadRateLimitStatus = async () => {
    try {
      const response = await mediaAPI.getRateLimitStatus();
      setRateLimitStatus(response.data);
    } catch (error) {
      console.error('Error loading rate limit status:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setFileUrl(''); // Clear URL if file is selected
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('media_type', mediaType);
      
      if (mediaType === 'text') {
        if (!textContent.trim()) {
          setError('Text content is required');
          setLoading(false);
          return;
        }
        formData.append('text_content', textContent);
      } else {
        if (!file && !fileUrl.trim()) {
          setError(`File or file URL is required for ${mediaType} analysis`);
          setLoading(false);
          return;
        }
        if (file) {
          formData.append('file', file);
        }
        if (fileUrl) {
          formData.append('file_url', fileUrl);
        }
      }
      
      if (organization) {
        formData.append('organization', organization);
      }

      const response = await mediaAPI.analyze(formData);
      onAnalysisComplete(response.data);
      
      // Reset form
      setTextContent('');
      setFile(null);
      setFileUrl('');
      setOrganization('');
      
      // Reload rate limit status
      await loadRateLimitStatus();
    } catch (err: any) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="media-analysis-form">
      <h3>Analyze Media with AI</h3>
      
      {rateLimitStatus && (
        <div className="rate-limit-info">
          <span>Remaining requests: <strong>{rateLimitStatus.remaining_requests}</strong> / {rateLimitStatus.limit_per_hour}</span>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Media Type *</label>
          <select
            value={mediaType}
            onChange={(e) => setMediaType(e.target.value as any)}
            className="form-control"
          >
            <option value="text">Text</option>
            <option value="image">Image</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
          </select>
        </div>

        {mediaType === 'text' ? (
          <div className="form-group">
            <label>Text Content *</label>
            <textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="Paste suspicious text, email content, or message here..."
              className="form-control"
              rows={8}
              required
            />
          </div>
        ) : (
          <>
            <div className="form-group">
              <label>Upload File</label>
              <input
                type="file"
                onChange={handleFileChange}
                accept={
                  mediaType === 'image' ? 'image/*' :
                  mediaType === 'audio' ? 'audio/*' :
                  mediaType === 'video' ? 'video/*' : '*'
                }
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>Or Provide URL</label>
              <input
                type="url"
                value={fileUrl}
                onChange={(e) => {
                  setFileUrl(e.target.value);
                  setFile(null); // Clear file if URL is provided
                }}
                placeholder={`Enter ${mediaType} URL...`}
                className="form-control"
              />
            </div>
          </>
        )}

        <div className="form-group">
          <label>Organization (optional)</label>
          <input
            type="text"
            value={organization}
            onChange={(e) => setOrganization(e.target.value)}
            placeholder="Organization name"
            className="form-control"
          />
        </div>

        <button
          type="submit"
          className="btn-submit"
          disabled={loading || (rateLimitStatus && rateLimitStatus.remaining_requests === 0)}
        >
          {loading ? 'Analyzing...' : 'Analyze with AI'}
        </button>
      </form>
    </div>
  );
};

export default MediaAnalysisForm;


