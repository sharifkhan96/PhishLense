from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db import models as django_models
from .models import TrafficEvent, ThreatTimeline
from .serializers import TrafficEventSerializer, TrafficEventSubmissionSerializer
from .services import ThreatAnalyzer, SandboxExecutor
from .ml_service import ml_service


class TrafficEventViewSet(viewsets.ModelViewSet):
    """ViewSet for managing traffic events"""
    queryset = TrafficEvent.objects.all()
    serializer_class = TrafficEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter events by user or show public events"""
        # Show events for the logged-in user OR events without a user (public/external events)
        # In production, you might want to filter by organization instead
        queryset = TrafficEvent.objects.filter(
            django_models.Q(user=self.request.user) | django_models.Q(user__isnull=True)
        )
        
        # Filter by classification if provided
        classification = self.request.query_params.get('classification', None)
        if classification:
            queryset = queryset.filter(classification=classification)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set user when creating event"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def receive(self, request):
        """
        Receive traffic from external sources (email, webhook, etc.)
        This endpoint doesn't require authentication for external integrations
        """
        serializer = TrafficEventSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Create traffic event
        event = TrafficEvent.objects.create(
            source_ip=data['source_ip'],
            destination_ip=data.get('destination_ip'),
            port=data.get('port'),
            payload=data['payload'],
            payload_type=data.get('payload_type', 'unknown'),
            organization=data.get('organization', ''),
            date_time=timezone.now()
        )
        
        # Analyze using ML model
        ml_result = ml_service.predict(
            source_ip=event.source_ip,
            destination_ip=event.destination_ip or '',
            payload=event.payload,
            payload_type=event.payload_type,
            port=event.port or 0,
            date_time=event.date_time
        )
        
        event.ml_prediction = ml_result.get('prediction', 'unknown')
        event.ml_confidence = ml_result.get('confidence', 0.0)
        
        # Determine if payload type is phishing-related (fallback if ML doesn't work)
        # Phishing attacks focus on: emails, links, text content, images, audio, video
        phishing_payload_types = [
            'phishing', 'phishing_email', 'suspicious_email', 'malicious_email',
            'phishing_link', 'suspicious_link', 'malicious_url', 'phishing_url',
            'phishing_text', 'suspicious_text', 'social_engineering',
            'phishing_image', 'suspicious_image', 'qr_code_phishing',
            'phishing_audio', 'suspicious_audio', 'voice_phishing', 'vishing',
            'phishing_video', 'suspicious_video',
            'credential_harvesting', 'fake_login', 'spoofed_site',
            'email_spoofing', 'brand_impersonation', 'urgent_action_required'
        ]
        is_phishing_payload = event.payload_type.lower() in [pt.lower() for pt in phishing_payload_types]
        
        # Determine classification based on ML prediction and payload type
        # Priority: ML prediction > payload type check
        if event.ml_prediction == 'malicious' or is_phishing_payload:
            analyzer = ThreatAnalyzer()
            # Convert to threat format for analysis
            threat_data = {
                'threat_type': 'text',
                'content': event.payload,
                'source': event.source_ip
            }
            # Run AI analysis (simplified)
            event.classification = 'malicious'
            event.status = 'analyzing'
            # Set severity based on phishing payload type
            if event.payload_type.lower() in ['credential_harvesting', 'fake_login', 'email_spoofing']:
                event.severity = 'critical'
            elif event.payload_type.lower() in ['phishing_email', 'phishing_link', 'phishing_url', 'brand_impersonation']:
                event.severity = 'high'
            else:
                event.severity = 'medium'
            event.save()
            
            # Run AI analysis in background (simplified for hackathon)
            try:
                # Create a temporary threat for analysis
                from .models import Threat
                temp_threat = Threat.objects.create(
                    threat_type='text',
                    content=event.payload,
                    source=event.source_ip
                )
                analysis_result = analyzer.analyze(temp_threat)
                
                if analysis_result.get('success'):
                    event.ai_analysis = temp_threat.ai_analysis
                    event.ai_explanation = temp_threat.ai_explanation
                    event.risk_score = temp_threat.risk_score
                    event.severity = temp_threat.severity
                    event.recommendations = temp_threat.recommendations
                
                temp_threat.delete()  # Clean up
            except Exception as e:
                print(f"Error in AI analysis: {e}")
        elif event.ml_prediction == 'normal':
            # ML predicts normal - trust the model
            event.classification = 'normal'
            event.severity = ''
        else:
            # ML prediction is unknown or not available
            if is_phishing_payload:
                # If payload type is phishing but ML didn't catch it, still mark as malicious
                event.classification = 'malicious'
                event.severity = 'medium'
            else:
                # Unknown classification
                event.classification = 'unknown'
        
        event.status = 'completed'
        event.analyzed_at = timezone.now()
        event.save()
        
        serializer = TrafficEventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get traffic statistics"""
        queryset = self.get_queryset()
        
        total = queryset.count()
        normal = queryset.filter(classification='normal').count()
        malicious = queryset.filter(classification='malicious').count()
        unknown = queryset.filter(classification='unknown').count()
        
        by_payload_type = {}
        for event in queryset.values('payload_type').distinct():
            payload_type = event['payload_type']
            by_payload_type[payload_type] = queryset.filter(payload_type=payload_type).count()
        
        return Response({
            'total': total,
            'normal': normal,
            'malicious': malicious,
            'unknown': unknown,
            'by_payload_type': by_payload_type
        })
    
    @action(detail=True, methods=['post'])
    def execute_sandbox(self, request, pk=None):
        """Execute event in sandbox"""
        event = self.get_object()
        
        if event.sandbox_executed:
            return Response(
                {'message': 'Event has already been executed in sandbox'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        executor = SandboxExecutor()
        # Convert event to threat format for sandbox
        from .models import Threat
        import re
        
        # Extract URL from payload if it contains one (more robust pattern)
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]()]+|www\.[^\s<>"{}|\\^`\[\]()]+|bit\.ly/[^\s<>"{}|\\^`\[\]()]+|tinyurl\.com/[^\s<>"{}|\\^`\[\]()]+|goo\.gl/[^\s<>"{}|\\^`\[\]()]+|t\.co/[^\s<>"{}|\\^`\[\]()]+'
        urls = re.findall(url_pattern, event.payload, re.IGNORECASE)
        
        # Clean up URLs (add http:// if missing)
        cleaned_urls = []
        for url in urls:
            if not url.startswith('http'):
                url = 'http://' + url
            cleaned_urls.append(url)
        
        # Determine threat type - prefer 'url' if URL found, or check payload_type
        if cleaned_urls:
            threat_type = 'url'
            content = cleaned_urls[0]  # Use first URL found
            print(f"🔗 Extracted URL from payload: {content}")
        elif 'http' in event.payload.lower() or 'www.' in event.payload.lower():
            # Try to extract URL more carefully
            url_match = re.search(r'(https?://[^\s<>"{}|\\^`\[\]()]+)', event.payload, re.IGNORECASE)
            if url_match:
                threat_type = 'url'
                content = url_match.group(1)
                print(f"🔗 Extracted URL from payload (method 2): {content}")
            else:
                threat_type = 'text'
                content = event.payload
                print(f"⚠️ No valid URL found in payload, treating as text")
        elif event.payload_type.lower() in ['link', 'url']:
            threat_type = 'url'
            content = event.payload
            print(f"🔗 Using payload as URL (payload_type={event.payload_type}): {content}")
        else:
            threat_type = 'text'
            content = event.payload
            print(f"⚠️ Threat type is '{event.payload_type}', sandbox may not execute")
        
        temp_threat = Threat.objects.create(
            threat_type=threat_type,
            content=content,
            source=event.source_ip
        )
        
        print(f"📦 Created threat: type={threat_type}, content_length={len(content)}")
        
        try:
            results = executor.execute(temp_threat)
            
            # Ensure results is a dict
            if not isinstance(results, dict):
                results = {'success': False, 'error': 'Invalid results format', 'actions_taken': [], 'observations': [], 'errors': [str(results)]}
            
            event.sandbox_executed = True
            event.sandbox_results = results
            event.actions_taken = results.get('actions_taken', [])
            event.save()
            
            print(f"✅ Sandbox execution completed for event {event.id}")
            print(f"   Actions: {len(results.get('actions_taken', []))}")
            print(f"   Observations: {len(results.get('observations', []))}")
            print(f"   Redirects: {len(results.get('redirects', []))}")
            print(f"   Forms: {len(results.get('forms_found', []))}")
            
        except Exception as e:
            print(f"❌ Error in sandbox execution: {e}")
            import traceback
            traceback.print_exc()
            results = {
                'success': False,
                'error': str(e),
                'actions_taken': [],
                'observations': [],
                'errors': [str(e)]
            }
            event.sandbox_executed = True
            event.sandbox_results = results
            event.save()
        finally:
            temp_threat.delete()
        
        serializer = TrafficEventSerializer(event)
        return Response(serializer.data)

