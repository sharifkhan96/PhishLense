"""
Views for media analysis
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import os
from .media_models import MediaAnalysis
from .media_serializers import MediaAnalysisSerializer
from .openai_service import openai_analyzer
import os


class MediaAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for media analysis"""
    queryset = MediaAnalysis.objects.all()
    serializer_class = MediaAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user"""
        return MediaAnalysis.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        """Add request to serializer context for file URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request):
        """Create and analyze media"""
        # Handle file upload
        file = request.FILES.get('file')
        media_type = request.data.get('media_type')
        text_content = request.data.get('text_content', '')
        file_url = request.data.get('file_url', '')
        organization = request.data.get('organization', '')
        
        if not media_type:
            return Response(
                {'error': 'media_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate inputs based on media type
        if media_type == 'text' and not text_content:
            return Response(
                {'error': 'text_content is required for text analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if media_type in ['image', 'video', 'audio'] and not file and not file_url:
            return Response(
                {'error': f'file or file_url is required for {media_type} analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create media analysis record
        media_analysis = MediaAnalysis.objects.create(
            media_type=media_type,
            text_content=text_content,
            file_url=file_url,
            file=file,
            user=request.user,
            organization=organization,
            status='analyzing'
        )
        
        # Analyze using OpenAI
        file_path = None
        file_url_for_analysis = file_url
        
        if file:
            # Ensure file is saved
            media_analysis.save()  # Save again to ensure file is written to disk
            
            # Try to get file path first
            file_path = None
            try:
                file_path = media_analysis.file.path
                # Verify file exists
                if not os.path.exists(file_path):
                    print(f"⚠️ File path exists but file not found: {file_path}")
                    file_path = None  # Will fall back to URL
            except Exception as path_error:
                print(f"⚠️ Could not get file path: {path_error}")
                file_path = None  # Will fall back to URL
            
            # If file_path failed, use URL instead
            if not file_path:
                try:
                    request_scheme = 'https' if request.is_secure() else 'http'
                    file_url_for_analysis = f"{request_scheme}://{request.get_host()}{media_analysis.file.url}"
                    print(f"✅ Using file URL instead: {file_url_for_analysis}")
                except Exception as url_error:
                    media_analysis.status = 'error'
                    media_analysis.error_message = f'Could not access file: {str(path_error) if path_error else str(url_error)}'
                    media_analysis.save()
                    return Response(
                        {'error': f'Could not access uploaded file. Please try again.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        elif not file_url_for_analysis and media_analysis.file:
            # Build URL for uploaded file (if file was set but no URL provided)
            try:
                request_scheme = 'https' if request.is_secure() else 'http'
                file_url_for_analysis = f"{request_scheme}://{request.get_host()}{media_analysis.file.url}"
            except:
                pass
        
        # Debug logging
        print(f"🔍 Starting analysis:")
        print(f"   Media type: {media_type}")
        print(f"   File path: {file_path}")
        print(f"   File URL: {file_url_for_analysis}")
        print(f"   User ID: {request.user.id}")
        
        analysis_result = openai_analyzer.analyze(
            media_type=media_type,
            content=text_content,
            file_path=file_path,
            file_url=file_url_for_analysis,
            user_id=request.user.id
        )
        
        print(f"📊 Analysis result: success={analysis_result.get('success')}, error={analysis_result.get('error')}")
        
        # Update with results
        if analysis_result.get('success'):
            media_analysis.what_received = analysis_result.get('what_received', '')
            media_analysis.what_did = analysis_result.get('what_did', '')
            media_analysis.what_to_do_next = analysis_result.get('what_to_do_next', '')
            media_analysis.ai_analysis = analysis_result.get('ai_analysis', '')
            media_analysis.risk_score = analysis_result.get('risk_score')
            media_analysis.is_threat = analysis_result.get('is_threat', False)
            media_analysis.threat_details = analysis_result.get('threat_details', {})
            media_analysis.status = 'completed'
            media_analysis.analyzed_at = timezone.now()
        else:
            media_analysis.status = 'error'
            error_msg = analysis_result.get('error', 'Analysis failed')
            media_analysis.error_message = error_msg
            # Log error for debugging
            print(f"❌ Media analysis error: {error_msg}")
            print(f"   Media type: {media_type}")
            print(f"   File path: {file_path}")
            print(f"   File URL: {file_url_for_analysis}")
            print(f"   Full analysis result: {analysis_result}")
        
        media_analysis.save()
        
        serializer = MediaAnalysisSerializer(media_analysis, context={'request': request})
        
        # If there was an error, return error status with detailed error message
        if media_analysis.status == 'error':
            return Response(
                {
                    **serializer.data,
                    'error': error_msg,
                    'error_message': error_msg
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def rate_limit_status(self, request):
        """Get current rate limit status"""
        remaining = openai_analyzer.get_remaining_requests(user_id=request.user.id)
        return Response({
            'remaining_requests': remaining,
            'limit_per_hour': int(os.getenv('OPENAI_RATE_LIMIT_PER_USER', 20))
        })

