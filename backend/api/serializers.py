from rest_framework import serializers
from .models import Threat, ThreatTimeline, TrafficEvent


class ThreatTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatTimeline
        fields = ['id', 'event_type', 'description', 'timestamp', 'metadata']


class ThreatSerializer(serializers.ModelSerializer):
    timeline_events = ThreatTimelineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Threat
        fields = [
            'id', 'threat_type', 'content', 'source', 'status', 'severity',
            'ai_analysis', 'ai_explanation', 'risk_score',
            'sandbox_executed', 'sandbox_results', 'actions_taken', 'observations',
            'recommendations', 'created_at', 'updated_at', 'analyzed_at',
            'timeline_events'
        ]
        read_only_fields = [
            'status', 'severity', 'ai_analysis', 'ai_explanation', 'risk_score',
            'sandbox_executed', 'sandbox_results', 'actions_taken', 'observations',
            'recommendations', 'analyzed_at', 'timeline_events'
        ]


class ThreatAnalysisRequestSerializer(serializers.Serializer):
    threat_type = serializers.ChoiceField(choices=['email', 'url', 'text', 'link'])
    content = serializers.CharField()
    source = serializers.CharField(required=False, allow_blank=True)
    execute_in_sandbox = serializers.BooleanField(default=True)


class TrafficEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficEvent
        fields = [
            'id', 'source_ip', 'destination_ip', 'port', 'payload', 'payload_type',
            'date_time', 'ml_prediction', 'ml_confidence', 'ai_analysis', 'ai_explanation',
            'status', 'classification', 'severity', 'risk_score', 'actions_taken',
            'sandbox_executed', 'sandbox_results', 'recommendations', 'organization',
            'created_at', 'updated_at', 'analyzed_at'
        ]
        read_only_fields = [
            'ml_prediction', 'ml_confidence', 'ai_analysis', 'ai_explanation',
            'status', 'classification', 'severity', 'risk_score', 'actions_taken',
            'sandbox_executed', 'sandbox_results', 'recommendations', 'analyzed_at'
        ]


class TrafficEventSubmissionSerializer(serializers.Serializer):
    """Serializer for receiving traffic from external sources"""
    source_ip = serializers.IPAddressField(required=True)
    destination_ip = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # Can be IP or email
    port = serializers.IntegerField(required=False, allow_null=True)
    payload = serializers.CharField(required=True)
    payload_type = serializers.CharField(required=False, default='unknown')
    organization = serializers.CharField(required=False, allow_blank=True)

