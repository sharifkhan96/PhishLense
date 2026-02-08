"""
OpenAI Multi-Modal Analysis Service with Rate Limiting
"""
import openai
import base64
import os
import json
import re
import mimetypes
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from typing import Dict, Optional, Tuple
from datetime import timedelta


class RateLimiter:
    """Simple rate limiter using Django cache"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Check if request is allowed
        Returns: (is_allowed, remaining_requests)
        """
        cache_key = f"rate_limit:{key}"
        current = cache.get(cache_key, 0)
        
        if current >= self.max_requests:
            return False, 0
        
        # Increment counter
        cache.set(cache_key, current + 1, self.window_seconds)
        return True, self.max_requests - (current + 1)
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window"""
        cache_key = f"rate_limit:{key}"
        current = cache.get(cache_key, 0)
        return max(0, self.max_requests - current)


class OpenAIMediaAnalyzer:
    """Analyze media (text, images, video, audio) using OpenAI API"""
    
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            print("⚠️ WARNING: OPENAI_API_KEY is not set in settings!")
        else:
            print(f"✅ OpenAI API key loaded (length: {len(api_key)})")
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
        # Rate limiting: per user
        # Default: 20 requests per hour per user
        self.rate_limiter = RateLimiter(
            max_requests=int(os.getenv('OPENAI_RATE_LIMIT_PER_USER', 20)),
            window_seconds=3600  # 1 hour
        )
    
    def analyze(self, media_type: str, content=None, file_path=None, file_url=None, user_id=None) -> Dict:
        """
        Analyze media using OpenAI
        
        Args:
            media_type: 'text', 'image', 'video', 'audio'
            content: Text content (for text type)
            file_path: Path to uploaded file
            file_url: URL to media file
            user_id: User ID for rate limiting
        
        Returns:
            Dict with analysis results
        """
        # Rate limiting check
        rate_key = f"user_{user_id}" if user_id else "anonymous"
        is_allowed, remaining = self.rate_limiter.is_allowed(rate_key)
        
        if not is_allowed:
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'message': f'You have exceeded the rate limit. Please try again later.',
                'remaining': 0
            }
        
        try:
            if media_type == 'text':
                return self._analyze_text(content, remaining)
            elif media_type == 'image':
                result = self._analyze_image(file_path, file_url, remaining)
                print(f"🖼️ Image analysis result: {result.get('success')}, error: {result.get('error')}")
                return result
            elif media_type == 'audio':
                return self._analyze_audio(file_path, file_url, remaining)
            elif media_type == 'video':
                return self._analyze_video(file_path, file_url, remaining)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported media type: {media_type}'
                }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Exception in analyze(): {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Analysis error: {error_msg}',
                'remaining': remaining
            }
    
    def _analyze_text(self, text: str, remaining: int) -> Dict:
        """Analyze text content"""
        if not text:
            return {'success': False, 'error': 'No text content provided'}
        
        prompt = f"""Analyze this content for security threats, phishing attempts, malicious links, or suspicious patterns.

Content:
{text[:4000]}  # Limit to 4000 chars

Provide:
1. A clear summary of what this content is
2. Any security threats or suspicious patterns detected
3. Risk assessment (0-100 score)
4. Recommended actions

Format your response as JSON:
{{
    "summary": "Brief summary",
    "is_threat": true/false,
    "risk_score": 0-100,
    "threats_detected": ["threat1", "threat2"],
    "recommendations": "What to do next"
}}"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Use latest model
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity expert analyzing content for threats. Provide clear, actionable analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse response
        try:
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = self._parse_text_response(analysis_text)
        except:
            data = self._parse_text_response(analysis_text)
        
        return {
            'success': True,
            'what_received': f"Text content ({len(text)} characters)",
            'what_did': "Analyzed text using GPT-4 for security threats and suspicious patterns",
            'what_to_do_next': data.get('recommendations', 'Review the analysis and take appropriate action.'),
            'ai_analysis': analysis_text,
            'risk_score': data.get('risk_score', 50),
            'is_threat': data.get('is_threat', False),
            'threat_details': data,
            'remaining': remaining
        }
    
    def _analyze_image(self, file_path=None, file_url=None, remaining: int = 0) -> Dict:
        """Analyze image using GPT-4 Vision"""
        if not file_path and not file_url:
            return {'success': False, 'error': 'No image provided'}
        
        # Prepare image
        image_url = None
        
        # Try file_path first (local file)
        if file_path:
            if os.path.exists(file_path):
                try:
                    # Check file size (OpenAI has limits, typically 20MB for images)
                    file_size = os.path.getsize(file_path)
                    max_size = 20 * 1024 * 1024  # 20MB
                    if file_size > max_size:
                        return {
                            'success': False,
                            'error': f'Image file too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 20MB.'
                        }
                    
                    # Read and encode image
                    print(f"📖 Reading image from path: {file_path} ({file_size} bytes)")
                    with open(file_path, 'rb') as image_file:
                        image_bytes = image_file.read()
                        image_data = base64.b64encode(image_bytes).decode('utf-8')
                        # Detect image format
                        mime_type, _ = mimetypes.guess_type(file_path)
                        if not mime_type or not mime_type.startswith('image/'):
                            mime_type = 'image/jpeg'  # Default to JPEG
                        image_url = f"data:{mime_type};base64,{image_data}"
                        print(f"✅ Image encoded successfully (base64 length: {len(image_data)})")
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ Error reading image file {file_path}: {error_msg}")
                    import traceback
                    traceback.print_exc()
                    # Fall back to URL if available
                    if file_url:
                        print(f"🔄 Falling back to file URL: {file_url}")
                        image_url = file_url
                    else:
                        return {
                            'success': False,
                            'error': f'Error reading image file: {error_msg}'
                        }
            else:
                print(f"⚠️ File path does not exist: {file_path}")
                # Fall back to URL if available
                if file_url:
                    print(f"🔄 Using file URL instead: {file_url}")
                    image_url = file_url
                else:
                    return {'success': False, 'error': 'Image file not found on disk'}
        
        # Use file_url if file_path didn't work or wasn't provided
        if not image_url and file_url:
            print(f"📎 Using file URL: {file_url}")
            image_url = file_url
        
        if not image_url:
            return {'success': False, 'error': 'Could not prepare image for analysis - neither file path nor URL worked'}
        
        prompt = """Analyze this image for security threats. Look for:
- Phishing attempts
- Suspicious QR codes
- Malicious links or URLs
- Social engineering content
- Any text that might indicate a security threat

Provide a detailed analysis in the following format:

**What I see:**
[Describe what's in the image]

**Threats detected:**
[List any security threats or suspicious elements]

**Risk score:** [0-100]
[Explain the risk level]

**Recommendations:**
[What actions should be taken]

If you find any threats, clearly state them. If the image appears safe, say so."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4 Vision model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert analyzing images for threats."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            print(f"📝 OpenAI response received ({len(analysis_text)} chars)")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ OpenAI API error for image analysis: {error_msg}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'OpenAI API error: {error_msg}',
                'what_received': 'Image file',
                'what_did': 'Attempted to analyze image using GPT-4 Vision',
                'what_to_do_next': 'Please check your OpenAI API key and try again. If the image is too large, try a smaller file.'
            }
        
        # Parse response - try to extract structured data
        data = self._parse_text_response(analysis_text)
        
        # Extract information from the analysis text
        what_received = self._extract_what_received(analysis_text) or "Image file"
        what_did = "Analyzed image using GPT-4 Vision for security threats, QR codes, and suspicious content"
        
        # Try to extract recommendations and risk score from the text
        recommendations = self._extract_recommendations(analysis_text)
        is_threat = self._detect_threat_in_text(analysis_text)
        
        # Extract risk score - use the most reliable method first
        # Priority: 1) JSON from _parse_text_response, 2) Direct extraction, 3) Fallback based on threat
        extracted_risk_score = self._extract_risk_score(analysis_text)
        
        # Determine final risk score with clear priority
        if data.get('risk_score') is not None:
            final_risk_score = int(data.get('risk_score'))
            print(f"📊 Using risk score from JSON parse: {final_risk_score}")
        elif extracted_risk_score is not None:
            final_risk_score = extracted_risk_score
            print(f"📊 Using risk score from direct extraction: {final_risk_score}")
        else:
            # Estimate risk score based on threat detection
            final_risk_score = 75 if is_threat else 25
            print(f"⚠️ Using fallback risk score: {final_risk_score} (threat={is_threat})")
        
        # Ensure risk score is within valid range
        final_risk_score = max(0, min(100, final_risk_score))
        print(f"🎯 Final risk score: {final_risk_score}")
        
        # Use parsed data if available, otherwise use extracted values
        what_to_do_next = data.get('recommendations') or recommendations
        if not what_to_do_next or len(what_to_do_next) < 10:
            # If we couldn't extract recommendations, use a summary of the analysis
            what_to_do_next = self._create_summary_recommendations(analysis_text, is_threat)
        
        final_is_threat = data.get('is_threat', False) or is_threat
        
        print(f"✅ Parsed: risk={final_risk_score} (from: {'JSON' if data.get('risk_score') is not None else 'extraction' if extracted_risk_score is not None else 'fallback'}), threat={final_is_threat}, recommendations={len(what_to_do_next)} chars")
        print(f"📄 Full analysis preview: {analysis_text[:200]}...")
        
        return {
            'success': True,
            'what_received': what_received,
            'what_did': what_did,
            'what_to_do_next': what_to_do_next,
            'ai_analysis': analysis_text,
            'risk_score': float(final_risk_score),  # Ensure it's a float for consistency
            'is_threat': final_is_threat,
            'threat_details': data,
            'remaining': remaining
        }
    
    def _analyze_audio(self, file_path=None, file_url=None, remaining: int = 0) -> Dict:
        """Analyze audio by transcribing first, then analyzing transcript"""
        if not file_path and not file_url:
            return {'success': False, 'error': 'No audio file provided'}
        
        # Step 1: Transcribe audio using Whisper
        try:
            if file_path:
                with open(file_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
            else:
                # For URL, we'd need to download first
                return {'success': False, 'error': 'URL audio transcription not yet supported'}
        except Exception as e:
            return {
                'success': False,
                'error': f'Audio transcription failed: {str(e)}'
            }
        
        # Step 2: Analyze transcript as text
        text_analysis = self._analyze_text(transcript, remaining)
        
        if text_analysis.get('success'):
            text_analysis['what_received'] = "Audio file (transcribed to text)"
            text_analysis['what_did'] = "Transcribed audio using Whisper, then analyzed transcript for security threats"
            text_analysis['transcript'] = transcript
        
        return text_analysis
    
    def _analyze_video(self, file_path=None, file_url=None, remaining: int = 0) -> Dict:
        """Analyze video by extracting frames and analyzing"""
        # For video, we'll extract key frames and analyze them
        # This is a simplified approach - in production, you might want more sophisticated frame extraction
        
        if not file_path and not file_url:
            return {'success': False, 'error': 'No video file provided'}
        
        # For now, return a message that video analysis needs frame extraction
        # In production, you'd use ffmpeg or similar to extract frames
        return {
            'success': False,
            'error': 'Video analysis requires frame extraction. This feature needs additional implementation.',
            'note': 'For MVP, consider extracting key frames first, then analyze as images'
        }
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse AI response to extract structured data"""
        import json
        import re
        
        result = {}
        
        # Try to extract JSON first
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except:
            pass
        
        # If no JSON, try to extract structured text
        # Extract risk score using the same method as _extract_risk_score
        risk_score_match = re.search(r'risk.*?score', text, re.IGNORECASE)
        if risk_score_match:
            start_pos = risk_score_match.end()
            remaining_text = text[start_pos:start_pos + 50]
            number_match = re.search(r'[:\s\*\*]+(\d+)', remaining_text)
            if number_match:
                try:
                    score = int(number_match.group(1))
                    if 0 <= score <= 100:
                        result['risk_score'] = score
                        print(f"✅ Parsed risk score from JSON fallback: {score}")
                except:
                    pass
        
        # Extract recommendations section
        rec_match = re.search(r'recommendations?[:\n]+(.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
        if rec_match:
            result['recommendations'] = rec_match.group(1).strip()
        
        return result
    
    def _extract_recommendations(self, text: str) -> str:
        """Extract recommendations from analysis text"""
        import re
        
        # Look for "Recommendations:" section
        patterns = [
            r'Recommendations?[:\n]+(.*?)(?:\n\n|\*\*|$)',
            r'What.*?do.*?next[:\n]+(.*?)(?:\n\n|\*\*|$)',
            r'Action.*?required[:\n]+(.*?)(?:\n\n|\*\*|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                rec = match.group(1).strip()
                if rec and len(rec) > 10:  # Make sure it's not empty
                    return rec
        
        return ""
    
    def _extract_risk_score(self, text: str) -> Optional[int]:
        """Extract risk score from analysis text"""
        import re
        
        # Strategy: Find "risk" and "score" together, then extract nearby number
        # Handle various formats: "Risk score: 85", "**Risk score:** 85", etc.
        
        # First, try to find "risk score" pattern (case insensitive)
        risk_score_match = re.search(r'risk.*?score', text, re.IGNORECASE)
        if risk_score_match:
            # Found "risk score", now look for number after it
            start_pos = risk_score_match.end()
            # Look for number in next 50 characters
            remaining_text = text[start_pos:start_pos + 50]
            number_match = re.search(r'[:\s\*\*]+(\d+)', remaining_text)
            if number_match:
                try:
                    score = int(number_match.group(1))
                    if 0 <= score <= 100:
                        print(f"✅ Extracted risk score: {score} (found after 'risk score')")
                        return score
                except:
                    pass
        
        # Fallback: Try direct patterns
        patterns = [
            r'score[:\s\*\*]+(\d+)',  # "score:" or "score**:" followed by number
            r'risk[:\s]+(\d+)/100',  # "risk: 85/100"
            r'risk.*?level[:\s]+(\d+)',  # "risk level: 85"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        print(f"✅ Extracted risk score: {score} using pattern")
                        return score
                except:
                    continue
        
        print(f"⚠️ Could not extract risk score. Text sample: {text[:200]}...")
        return None
    
    def _detect_threat_in_text(self, text: str) -> bool:
        """Detect if text indicates a threat"""
        import re
        
        threat_indicators = [
            r'threat',
            r'malicious',
            r'phishing',
            r'suspicious',
            r'attack',
            r'vulnerability',
            r'dangerous',
            r'compromised',
            r'fraudulent',
        ]
        
        safe_indicators = [
            r'no threat',
            r'no security',
            r'appears safe',
            r'legitimate',
            r'benign',
        ]
        
        text_lower = text.lower()
        
        # Check for explicit safe indicators first
        if any(re.search(pattern, text_lower) for pattern in safe_indicators):
            return False
        
        # Count threat indicators
        threat_count = sum(1 for pattern in threat_indicators if re.search(pattern, text_lower))
        
        # If multiple threat indicators, likely a threat
        return threat_count >= 2
    
    def _extract_what_received(self, text: str) -> str:
        """Extract description of what was received from analysis"""
        import re
        
        # Look for "What I see:" or similar patterns
        patterns = [
            r'What.*?see[:\n]+(.*?)(?:\n\n|\*\*|$)',
            r'Image.*?contains[:\n]+(.*?)(?:\n\n|\*\*|$)',
            r'This.*?image[:\n]+(.*?)(?:\n\n|\*\*|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                if desc and len(desc) > 10:
                    # Truncate if too long
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    return desc
        
        return ""
    
    def _create_summary_recommendations(self, text: str, is_threat: bool) -> str:
        """Create recommendations summary from analysis text"""
        import re
        
        # Try to extract key points
        sentences = text.split('.')
        key_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                # Look for action-oriented sentences
                if any(word in sentence.lower() for word in ['should', 'recommend', 'action', 'take', 'avoid', 'do not']):
                    key_sentences.append(sentence)
                    if len(key_sentences) >= 2:
                        break
        
        if key_sentences:
            return '. '.join(key_sentences) + '.'
        
        # Fallback based on threat status
        if is_threat:
            return "This image contains potential security threats. Review the full analysis above and take appropriate security measures. Do not interact with any suspicious links or QR codes shown in the image."
        else:
            return "The image appears safe, but review the full analysis for details. If you have any concerns, consult with your security team."
        
        # Fallback parsing
        risk_match = re.search(r'risk[_\s]?score[:\s]+(\d+)', text, re.IGNORECASE)
        risk_score = float(risk_match.group(1)) if risk_match else 50
        
        is_threat = any(word in text.lower() for word in ['threat', 'malicious', 'phishing', 'suspicious', 'dangerous'])
        
        return {
            'risk_score': risk_score,
            'is_threat': is_threat,
            'recommendations': 'Review the analysis and take appropriate action.'
        }
    
    def get_remaining_requests(self, user_id=None) -> int:
        """Get remaining requests for user"""
        rate_key = f"user_{user_id}" if user_id else "anonymous"
        return self.rate_limiter.get_remaining(rate_key)


# Global instance
openai_analyzer = OpenAIMediaAnalyzer()

