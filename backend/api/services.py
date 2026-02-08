"""
Core services for threat analysis and sandbox execution
"""
import openai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from django.conf import settings
from django.utils import timezone
from .models import Threat, ThreatTimeline, ThreatSeverity, ThreatStatus
import json
import re


class ThreatAnalyzer:
    """Analyzes threats using OpenAI API"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def analyze(self, threat: Threat) -> dict:
        """Analyze a threat and return analysis results"""
        
        # Create timeline event
        ThreatTimeline.objects.create(
            threat=threat,
            event_type='analysis_started',
            description='Started AI analysis of threat'
        )
        
        threat.status = ThreatStatus.ANALYZING
        threat.save()
        
        # Prepare prompt based on threat type
        prompt = self._build_analysis_prompt(threat)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert analyzing potential phishing and security threats. Provide detailed, actionable analysis."
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
            
            # Parse the analysis to extract structured data
            analysis_data = self._parse_analysis(analysis_text, threat)
            
            # Update threat with analysis results
            threat.ai_analysis = analysis_text
            threat.ai_explanation = analysis_data.get('explanation', analysis_text)
            threat.risk_score = analysis_data.get('risk_score', 50)
            threat.severity = analysis_data.get('severity', ThreatSeverity.MEDIUM)
            threat.recommendations = analysis_data.get('recommendations', 'Review the threat manually.')
            threat.analyzed_at = timezone.now()
            threat.status = ThreatStatus.COMPLETED
            threat.save()
            
            ThreatTimeline.objects.create(
                threat=threat,
                event_type='analysis_completed',
                description=f'AI analysis completed. Risk score: {threat.risk_score}, Severity: {threat.get_severity_display()}'
            )
            
            return {
                'success': True,
                'analysis': analysis_data
            }
            
        except Exception as e:
            threat.status = ThreatStatus.ERROR
            threat.save()
            ThreatTimeline.objects.create(
                threat=threat,
                event_type='analysis_error',
                description=f'Error during analysis: {str(e)}'
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_analysis_prompt(self, threat: Threat) -> str:
        """Build analysis prompt based on threat type"""
        base_prompt = f"""
Analyze this potential security threat:

Threat Type: {threat.get_threat_type_display()}
Source: {threat.source or 'Unknown'}
Content: {threat.content[:2000]}  # Limit content length

Please provide:
1. A risk score from 0-100 (where 0 is safe, 100 is critical threat)
2. Severity level: LOW, MEDIUM, HIGH, or CRITICAL
3. A clear explanation of what makes this suspicious or dangerous
4. Specific indicators of compromise or malicious behavior
5. Recommended actions for the organization

Format your response as JSON with the following structure:
{{
    "risk_score": <number>,
    "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "explanation": "<detailed explanation>",
    "indicators": ["<indicator1>", "<indicator2>", ...],
    "recommendations": "<actionable recommendations>"
}}
"""
        return base_prompt
    
    def _parse_analysis(self, analysis_text: str, threat: Threat) -> dict:
        """Parse AI analysis response to extract structured data"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'risk_score': float(data.get('risk_score', 50)),
                    'severity': data.get('severity', 'MEDIUM').lower(),
                    'explanation': data.get('explanation', analysis_text),
                    'indicators': data.get('indicators', []),
                    'recommendations': data.get('recommendations', 'Review manually.')
                }
        except:
            pass
        
        # Fallback: extract information using regex
        risk_match = re.search(r'risk[_\s]?score[:\s]+(\d+)', analysis_text, re.IGNORECASE)
        risk_score = float(risk_match.group(1)) if risk_match else 50
        
        severity_match = re.search(r'severity[:\s]+(LOW|MEDIUM|HIGH|CRITICAL)', analysis_text, re.IGNORECASE)
        severity = severity_match.group(1).lower() if severity_match else 'medium'
        
        return {
            'risk_score': risk_score,
            'severity': severity,
            'explanation': analysis_text,
            'indicators': [],
            'recommendations': 'Review the threat manually and take appropriate action.'
        }


class SandboxExecutor:
    """Executes threats in a sandboxed environment"""
    
    def __init__(self):
        self.max_redirects = settings.SANDBOX_MAX_REDIRECTS
        self.timeout = settings.SANDBOX_TIMEOUT
    
    def execute(self, threat: Threat) -> dict:
        """Execute threat in sandbox and return results"""
        
        ThreatTimeline.objects.create(
            threat=threat,
            event_type='sandbox_execution_started',
            description='Started sandbox execution'
        )
        
        threat.status = ThreatStatus.EXECUTING
        threat.save()
        
        results = {
            'success': False,
            'actions_taken': [],
            'observations': [],
            'redirects': [],
            'forms_found': [],
            'errors': []
        }
        
        try:
            if threat.threat_type in ['url', 'link']:
                results = self._execute_url(threat)
            elif threat.threat_type == 'email':
                results = self._execute_email(threat)
            else:
                results['observations'].append('Sandbox execution not applicable for this threat type')
            
            threat.sandbox_executed = True
            threat.sandbox_results = results
            threat.actions_taken = results.get('actions_taken', [])
            threat.observations = '\n'.join(results.get('observations', []))
            threat.status = ThreatStatus.COMPLETED
            threat.save()
            
            ThreatTimeline.objects.create(
                threat=threat,
                event_type='sandbox_execution_completed',
                description=f'Sandbox execution completed. Actions taken: {len(results.get("actions_taken", []))}'
            )
            
        except Exception as e:
            results['errors'].append(str(e))
            threat.sandbox_results = results
            threat.status = ThreatStatus.ERROR
            threat.save()
            
            ThreatTimeline.objects.create(
                threat=threat,
                event_type='sandbox_execution_error',
                description=f'Error during sandbox execution: {str(e)}'
            )
        
        return results
    
    def _execute_url(self, threat: Threat) -> dict:
        """Execute URL in sandbox"""
        url = threat.content.strip()
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            # Try to fix common URL issues
            if url.startswith('www.'):
                url = 'http://' + url
            elif '://' not in url:
                # Might be a domain or path
                if '.' in url and not url.startswith('/'):
                    url = 'http://' + url
                else:
                    return {
                        'success': False,
                        'actions_taken': [],
                        'observations': [f'Invalid URL format: {url}'],
                        'redirects': [],
                        'forms_found': [],
                        'errors': [f'URL must start with http:// or https://']
                    }
        
        print(f"🌐 Executing URL in sandbox: {url}")
        results = {
            'success': True,
            'actions_taken': [],
            'observations': [],
            'redirects': [],
            'forms_found': [],
            'errors': []
        }
        
        try:
            # Follow redirects
            current_url = url
            redirect_count = 0
            
            # Record initial attempt
            results['actions_taken'].append(f'Attempting to access URL: {current_url}')
            
            while redirect_count < self.max_redirects:
                try:
                    response = requests.get(
                        current_url,
                        timeout=self.timeout,
                        allow_redirects=False,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (PhishLense Sandbox)'
                        }
                    )
                    
                    results['actions_taken'].append(f'✅ Successfully accessed URL: {current_url}')
                    results['observations'].append(f'HTTP Status: {response.status_code}')
                    
                    # Check for redirects
                    if response.status_code in [301, 302, 303, 307, 308]:
                        redirect_url = response.headers.get('Location', '')
                        if redirect_url:
                            results['redirects'].append({
                                'from': current_url,
                                'to': redirect_url,
                                'status': response.status_code
                            })
                            current_url = urljoin(current_url, redirect_url)
                            redirect_count += 1
                            continue
                    
                    # Parse HTML content
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Find and submit forms with fake credentials
                        forms = soup.find_all('form')
                        for form in forms:
                            form_data = {
                                'action': form.get('action', ''),
                                'method': form.get('method', 'GET').upper(),
                                'fields': []
                            }
                            
                            # Build form data with fake credentials
                            form_payload = {}
                            for input_field in form.find_all(['input', 'textarea', 'select']):
                                field_name = input_field.get('name', '')
                                field_type = input_field.get('type', 'text').lower()
                                
                                form_data['fields'].append({
                                    'name': field_name,
                                    'type': field_type,
                                    'required': input_field.has_attr('required')
                                })
                                
                                # Fill with fake credentials based on field type/name
                                if field_name:
                                    if any(keyword in field_name.lower() for keyword in ['email', 'username', 'user', 'login']):
                                        form_payload[field_name] = 'sandbox_test_user@phishlense.com'
                                    elif any(keyword in field_name.lower() for keyword in ['password', 'pwd', 'pass']):
                                        form_payload[field_name] = 'FakePassword123!'
                                    elif any(keyword in field_name.lower() for keyword in ['card', 'credit', 'cvv', 'cvc']):
                                        form_payload[field_name] = '4111111111111111' if 'card' in field_name.lower() else '123'
                                    elif any(keyword in field_name.lower() for keyword in ['phone', 'mobile', 'tel']):
                                        form_payload[field_name] = '+1-555-0100'
                                    elif field_type == 'hidden':
                                        form_payload[field_name] = input_field.get('value', '')
                                    elif field_type in ['checkbox', 'radio']:
                                        if input_field.has_attr('checked'):
                                            form_payload[field_name] = input_field.get('value', 'on')
                                    else:
                                        form_payload[field_name] = f'test_{field_name}' if field_name else 'test_value'
                            
                            results['forms_found'].append(form_data)
                            results['actions_taken'].append(f'Found form with {len(form_data["fields"])} fields')
                            
                            # Submit form with fake credentials
                            if form_payload and form_data['action']:
                                try:
                                    form_action = urljoin(current_url, form_data['action'])
                                    submit_method = form_data['method']
                                    
                                    if submit_method == 'POST':
                                        submit_response = requests.post(
                                            form_action,
                                            data=form_payload,
                                            timeout=self.timeout,
                                            allow_redirects=False,
                                            headers={'User-Agent': 'Mozilla/5.0 (PhishLense Sandbox)'}
                                        )
                                    else:
                                        submit_response = requests.get(
                                            form_action,
                                            params=form_payload,
                                            timeout=self.timeout,
                                            allow_redirects=False,
                                            headers={'User-Agent': 'Mozilla/5.0 (PhishLense Sandbox)'}
                                        )
                                    
                                    results['actions_taken'].append(f'✅ Submitted form to {form_action} (method: {submit_method})')
                                    results['observations'].append(f'Form submission status: {submit_response.status_code}')
                                    
                                    # Check for redirects after form submission
                                    if submit_response.status_code in [301, 302, 303, 307, 308]:
                                        redirect_url = submit_response.headers.get('Location', '')
                                        if redirect_url:
                                            results['redirects'].append({
                                                'from': form_action,
                                                'to': redirect_url,
                                                'status': submit_response.status_code,
                                                'reason': 'Form submission redirect'
                                            })
                                            results['observations'].append(f'⚠️ Form submission redirected to: {redirect_url}')
                                    
                                    # Analyze response for suspicious content
                                    if 'text/html' in submit_response.headers.get('Content-Type', ''):
                                        response_soup = BeautifulSoup(submit_response.text, 'html.parser')
                                        response_text = response_soup.get_text().lower()
                                        
                                        if any(keyword in response_text for keyword in ['success', 'thank you', 'welcome', 'logged in']):
                                            results['observations'].append('⚠️ Form submission appears successful - potential credential harvesting!')
                                        
                                        # Check if redirected to a different domain
                                        if redirect_url and urlparse(redirect_url).netloc != urlparse(current_url).netloc:
                                            results['observations'].append(f'🚨 CRITICAL: Form redirected to different domain: {redirect_url}')
                                    
                                except Exception as e:
                                    results['errors'].append(f'Error submitting form: {str(e)}')
                                    results['actions_taken'].append(f'❌ Failed to submit form: {str(e)}')
                            
                            # Check for suspicious patterns in page content
                            suspicious_patterns = [
                                (r'password|pwd|passwd', 'Password field detected'),
                                (r'credit.?card|card.?number|cvv', 'Credit card field detected'),
                                (r'bank.?account|routing', 'Banking information field detected'),
                                (r'javascript:|onclick=|onerror=', 'Suspicious JavaScript detected'),
                            ]
                            
                            page_text = soup.get_text().lower()
                            for pattern, description in suspicious_patterns:
                                if re.search(pattern, page_text, re.IGNORECASE):
                                    results['observations'].append(f'⚠️ {description}')
                    else:
                        # Not HTML content
                        results['observations'].append(f'Response is not HTML (Content-Type: {response.headers.get("Content-Type", "unknown")})')
                    
                    break
                    
                except requests.exceptions.Timeout:
                    results['actions_taken'].append(f'⏱️ Request to {current_url} timed out')
                    results['observations'].append('⚠️ URL did not respond within timeout period')
                    results['errors'].append(f'Request to {current_url} timed out after {self.timeout}s')
                    results['success'] = True  # Still useful information
                    break
                except requests.exceptions.ConnectionError as e:
                    error_msg = str(e)
                    results['actions_taken'].append(f'❌ Failed to connect to {current_url}')
                    
                    # Provide more helpful error messages
                    if 'NameResolutionError' in error_msg or 'Failed to resolve' in error_msg:
                        results['observations'].append('🚨 DNS resolution failed - domain does not exist or is unreachable')
                        results['observations'].append('⚠️ This could indicate: fake domain, typo-squatting, or malicious site')
                    elif 'Connection refused' in error_msg:
                        results['observations'].append('🚨 Connection refused - server is not accepting connections')
                    else:
                        results['observations'].append(f'⚠️ Connection error: {error_msg}')
                    
                    results['errors'].append(f'Connection error: {error_msg}')
                    # Still mark as success for analysis purposes - we learned something
                    results['success'] = True  # Changed: even connection errors are useful info
                    break
                except requests.exceptions.RequestException as e:
                    results['actions_taken'].append(f'❌ Request to {current_url} failed')
                    results['observations'].append(f'⚠️ Request error: {str(e)}')
                    results['errors'].append(f'Request error: {str(e)}')
                    results['success'] = True  # Still useful information
                    break
                except Exception as e:
                    results['actions_taken'].append(f'❌ Unexpected error accessing {current_url}')
                    results['observations'].append(f'⚠️ Unexpected error: {str(e)}')
                    results['errors'].append(f'Unexpected error: {str(e)}')
                    results['success'] = True  # Still useful information
                    break
            
            results['observations'].append(f'Total redirects followed: {len(results["redirects"])}')
            
        except Exception as e:
            # Catch any other unexpected errors
            results['errors'].append(f'Unexpected error in sandbox execution: {str(e)}')
            results['success'] = False
        
        return results
    
    def _execute_email(self, threat: Threat) -> dict:
        """Extract and analyze URLs/links from email"""
        results = {
            'success': True,
            'actions_taken': [],
            'observations': [],
            'urls_found': [],
            'errors': []
        }
        
        # Extract URLs from email content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, threat.content)
        
        results['urls_found'] = urls
        results['observations'].append(f'Found {len(urls)} URLs in email')
        
        # Execute each URL found in email
        for url in urls[:3]:  # Limit to first 3 URLs
            url_results = self._execute_url_simple(url)
            results['actions_taken'].extend(url_results.get('actions_taken', []))
            results['observations'].extend(url_results.get('observations', []))
        
        return results
    
    def _execute_url_simple(self, url: str) -> dict:
        """Simple URL execution without full sandbox"""
        results = {
            'actions_taken': [],
            'observations': [],
            'errors': []
        }
        
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            results['actions_taken'].append(f'Accessed URL: {url}')
            results['observations'].append(f'Final URL: {response.url}')
            results['observations'].append(f'Status: {response.status_code}')
        except Exception as e:
            results['errors'].append(f'Error accessing {url}: {str(e)}')
        
        return results

