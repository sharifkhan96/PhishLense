from rest_framework import serializers
from .media_models import MediaAnalysis, MediaType


class MediaAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for media analysis"""
    media_type_display = serializers.CharField(source='get_media_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaAnalysis
        fields = [
            'id', 'media_type', 'media_type_display', 'file', 'file_url', 'text_content',
            'what_received', 'what_did', 'what_to_do_next',
            'ai_analysis', 'risk_score', 'is_threat', 'threat_details',
            'status', 'error_message', 'organization',
            'created_at', 'updated_at', 'analyzed_at'
        ]
        read_only_fields = [
            'what_received', 'what_did', 'what_to_do_next',
            'ai_analysis', 'risk_score', 'is_threat', 'threat_details',
            'status', 'error_message', 'analyzed_at'
        ]
    
    def get_file_url(self, obj):
        """Get full URL for file"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return obj.file_url


class MediaAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for media analysis request"""
    media_type = serializers.ChoiceField(choices=MediaType.choices)
    text_content = serializers.CharField(required=False, allow_blank=True)
    file_url = serializers.URLField(required=False, allow_blank=True)
    organization = serializers.CharField(required=False, allow_blank=True)


