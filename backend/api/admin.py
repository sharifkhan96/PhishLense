from django.contrib import admin
from .models import Threat, ThreatTimeline, TrafficEvent
from .media_models import MediaAnalysis


@admin.register(Threat)
class ThreatAdmin(admin.ModelAdmin):
    list_display = ['id', 'threat_type', 'source', 'severity', 'risk_score', 'status', 'created_at']
    list_filter = ['threat_type', 'severity', 'status', 'sandbox_executed']
    search_fields = ['content', 'source']
    readonly_fields = ['created_at', 'updated_at', 'analyzed_at']


@admin.register(ThreatTimeline)
class ThreatTimelineAdmin(admin.ModelAdmin):
    list_display = ['id', 'threat', 'event_type', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    readonly_fields = ['timestamp']


@admin.register(TrafficEvent)
class TrafficEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'source_ip', 'destination_ip', 'payload_type', 'classification', 'ml_prediction', 'severity', 'date_time']
    list_filter = ['classification', 'payload_type', 'severity', 'ml_prediction', 'sandbox_executed']
    search_fields = ['source_ip', 'destination_ip', 'payload']
    readonly_fields = ['created_at', 'updated_at', 'analyzed_at']
    date_hierarchy = 'date_time'


@admin.register(MediaAnalysis)
class MediaAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'media_type', 'user', 'status', 'is_threat', 'risk_score', 'created_at']
    list_filter = ['media_type', 'status', 'is_threat']
    search_fields = ['text_content', 'organization']
    readonly_fields = ['created_at', 'updated_at', 'analyzed_at']
    date_hierarchy = 'created_at'

