from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Threat, ThreatTimeline, ThreatSeverity, ThreatType
from .serializers import ThreatSerializer, ThreatAnalysisRequestSerializer
from .services import ThreatAnalyzer, SandboxExecutor


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint showing available endpoints"""
    return Response({
        'message': 'PhishLense API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'current_user': '/api/auth/me/',
                'refresh_token': '/api/auth/refresh/',
            },
            'traffic_events': {
                'list': '/api/traffic/',
                'receive': '/api/traffic/receive/',
                'stats': '/api/traffic/stats/',
                'detail': '/api/traffic/{id}/',
            },
            'media_analysis': {
                'list': '/api/media/',
                'analyze': '/api/media/',
                'detail': '/api/media/{id}/',
                'rate_limit': '/api/media/rate_limit_status/',
            },
            'threats': {
                'list': '/api/threats/',
                'create': '/api/threats/',
                'detail': '/api/threats/{id}/',
                'stats': '/api/threats/stats/',
            }
        },
        'documentation': 'See README.md for API usage examples'
    })


class ThreatViewSet(viewsets.ModelViewSet):
    """ViewSet for managing threats"""
    queryset = Threat.objects.all()
    serializer_class = ThreatSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Create and analyze a new threat"""
        serializer = ThreatAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Create threat
        threat = Threat.objects.create(
            threat_type=data['threat_type'],
            content=data['content'],
            source=data.get('source', '')
        )
        
        ThreatTimeline.objects.create(
            threat=threat,
            event_type='threat_received',
            description=f'New {threat.get_threat_type_display()} threat received from {threat.source or "unknown source"}'
        )
        
        # Analyze threat
        analyzer = ThreatAnalyzer()
        analysis_result = analyzer.analyze(threat)
        
        # Execute in sandbox if requested
        if data.get('execute_in_sandbox', True) and threat.threat_type in ['url', 'link', 'email']:
            executor = SandboxExecutor()
            executor.execute(threat)
        
        # Return threat with analysis
        threat.refresh_from_db()
        serializer = ThreatSerializer(threat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute threat in sandbox"""
        threat = self.get_object()
        
        if threat.sandbox_executed:
            return Response(
                {'message': 'Threat has already been executed in sandbox'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        executor = SandboxExecutor()
        results = executor.execute(threat)
        
        threat.refresh_from_db()
        serializer = ThreatSerializer(threat)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reanalyze(self, request, pk=None):
        """Re-analyze a threat"""
        threat = self.get_object()
        
        analyzer = ThreatAnalyzer()
        analysis_result = analyzer.analyze(threat)
        
        threat.refresh_from_db()
        serializer = ThreatSerializer(threat)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about threats"""
        total = Threat.objects.count()
        by_severity = {}
        for severity, _ in ThreatSeverity.choices:
            by_severity[severity] = Threat.objects.filter(severity=severity).count()
        
        by_type = {}
        for threat_type, _ in ThreatType.choices:
            by_type[threat_type] = Threat.objects.filter(threat_type=threat_type).count()
        
        return Response({
            'total': total,
            'by_severity': by_severity,
            'by_type': by_type,
            'sandbox_executed': Threat.objects.filter(sandbox_executed=True).count()
        })
