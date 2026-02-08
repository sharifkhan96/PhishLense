# OpenAI Multi-Modal Analysis Integration

## ✅ Completed Features

### 1. Multi-Modal Analysis Support
- **Text Analysis**: Analyzes text content for security threats
- **Image Analysis**: Uses GPT-4 Vision to analyze images for:
  - Phishing attempts
  - Suspicious QR codes
  - Malicious links or URLs
  - Social engineering content
- **Audio Analysis**: Transcribes audio using Whisper, then analyzes transcript
- **Video Analysis**: Framework ready (needs frame extraction implementation)

### 2. Rate Limiting
- Per-user rate limiting (default: 20 requests/hour)
- Configurable via `OPENAI_RATE_LIMIT_PER_USER` in `.env`
- Uses Django cache for tracking
- Returns remaining requests in API responses

### 3. User Feedback System
Each analysis provides three key pieces of feedback:
- **📥 What Received**: Description of what was analyzed
- **⚙️ What Did**: What actions the system took
- **➡️ What to Do Next**: Recommended next steps

### 4. Dashboard Integration
- New "Media Analysis" tab in dashboard
- File upload form for images, audio, video
- Text input for text analysis
- Real-time display of analysis results
- Rate limit status indicator

## API Endpoints

### Analyze Media
```bash
POST /api/media/
Content-Type: multipart/form-data

# For text
media_type=text
text_content=Your suspicious text here

# For image/audio/video
media_type=image
file=<file>
# OR
file_url=https://example.com/image.jpg
```

### Get Rate Limit Status
```bash
GET /api/media/rate_limit_status/
Authorization: Bearer <token>

Response:
{
  "remaining_requests": 15,
  "limit_per_hour": 20
}
```

### List All Analyses
```bash
GET /api/media/
Authorization: Bearer <token>
```

## Configuration

Add to your `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_RATE_LIMIT_PER_USER=20  # Requests per hour per user
```

## Usage

1. **Via Dashboard**:
   - Go to Dashboard → Media Analysis tab
   - Click "Analyze Media"
   - Upload file or paste text
   - View results with feedback

2. **Via API**:
   ```bash
   curl -X POST http://localhost:8000/api/media/ \
     -H "Authorization: Bearer <token>" \
     -F "media_type=text" \
     -F "text_content=Suspicious email content here"
   ```

## Models

- `MediaAnalysis`: Stores analysis requests and results
- Fields include: what_received, what_did, what_to_do_next, risk_score, is_threat

## Rate Limiting Details

- Uses Django's cache framework (LocMemCache by default)
- Sliding window: 1 hour
- Per-user tracking
- Returns error when limit exceeded with clear message

## Next Steps (Future Enhancements)

1. **Video Analysis**: Implement frame extraction for video files
2. **Async Processing**: Move to Celery for long-running analyses
3. **Cost Tracking**: Track OpenAI API costs per user/organization
4. **Advanced Rate Limiting**: Tiered limits (free vs paid users)
5. **Batch Analysis**: Analyze multiple files at once


