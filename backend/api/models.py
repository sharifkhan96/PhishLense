from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ThreatType(models.TextChoices):
    EMAIL = 'email', 'Email'
    URL = 'url', 'URL'
    TEXT = 'text', 'Text'
    LINK = 'link', 'Link'


class ThreatStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Analysis'
    ANALYZING = 'analyzing', 'Analyzing'
    EXECUTING = 'executing', 'Executing in Sandbox'
    COMPLETED = 'completed', 'Analysis Completed'
    ERROR = 'error', 'Error'


class ThreatSeverity(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class Threat(models.Model):
    """Represents a potential security threat"""
    threat_type = models.CharField(max_length=20, choices=ThreatType.choices)
    content = models.TextField(help_text="The suspicious content (email body, URL, text, etc.)")
    source = models.CharField(max_length=255, blank=True, help_text="Source identifier (sender email, domain, etc.)")
    status = models.CharField(max_length=20, choices=ThreatStatus.choices, default=ThreatStatus.PENDING)
    severity = models.CharField(max_length=20, choices=ThreatSeverity.choices, blank=True)
    
    # AI Analysis Results
    ai_analysis = models.TextField(blank=True, help_text="AI-generated threat analysis")
    ai_explanation = models.TextField(blank=True, help_text="Human-readable explanation of the threat")
    risk_score = models.FloatField(null=True, blank=True, help_text="Risk score from 0-100")
    
    # Sandbox Execution Results
    sandbox_executed = models.BooleanField(default=False)
    sandbox_results = models.JSONField(default=dict, blank=True, help_text="Results from sandbox execution")
    actions_taken = models.JSONField(default=list, blank=True, help_text="List of actions taken in sandbox")
    observations = models.TextField(blank=True, help_text="Observations from sandbox execution")
    
    # Recommendations
    recommendations = models.TextField(blank=True, help_text="Recommended actions for the organization")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_threat_type_display()} - {self.source or 'Unknown'} - {self.get_severity_display() or 'Unanalyzed'}"


class ThreatTimeline(models.Model):
    """Timeline events for a threat analysis"""
    threat = models.ForeignKey(Threat, on_delete=models.CASCADE, related_name='timeline_events')
    event_type = models.CharField(max_length=50, help_text="Type of event (analysis_started, sandbox_executed, etc.)")
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.threat} - {self.event_type} at {self.timestamp}"


class TrafficEvent(models.Model):
    """Represents incoming traffic/attack events with ML model fields"""
    # Traffic/Network Fields (for ML model)
    source_ip = models.GenericIPAddressField(help_text="Source IP address")
    destination_ip = models.CharField(max_length=255, null=True, blank=True, help_text="Destination IP address or email")
    port = models.IntegerField(null=True, blank=True, help_text="Port number")
    payload = models.TextField(help_text="The payload/request content")
    payload_type = models.CharField(max_length=50, help_text="Type of payload (SQLi, XSS, etc.)")
    date_time = models.DateTimeField(auto_now_add=True, help_text="Date and time of the event")
    
    # Analysis Results
    ml_prediction = models.CharField(max_length=20, blank=True, help_text="ML model prediction (normal/malicious)")
    ml_confidence = models.FloatField(null=True, blank=True, help_text="ML model confidence score")
    ai_analysis = models.TextField(blank=True, help_text="AI-generated analysis")
    ai_explanation = models.TextField(blank=True, help_text="Human-readable explanation")
    
    # Status and Classification
    status = models.CharField(max_length=20, choices=ThreatStatus.choices, default=ThreatStatus.PENDING)
    classification = models.CharField(max_length=20, default='unknown', help_text="Final classification: normal/malicious/unknown")
    severity = models.CharField(max_length=20, choices=ThreatSeverity.choices, blank=True)
    risk_score = models.FloatField(null=True, blank=True, help_text="Risk score from 0-100")
    
    # Actions Taken
    actions_taken = models.JSONField(default=list, blank=True, help_text="Actions taken by the system")
    sandbox_executed = models.BooleanField(default=False)
    sandbox_results = models.JSONField(default=dict, blank=True)
    
    # Recommendations
    recommendations = models.TextField(blank=True, help_text="What to do next")
    
    # User/Organization
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='traffic_events', null=True, blank=True)
    organization = models.CharField(max_length=255, blank=True, help_text="Organization identifier")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_time']
        indexes = [
            models.Index(fields=['-date_time']),
            models.Index(fields=['source_ip']),
            models.Index(fields=['classification']),
        ]
    
    def __str__(self):
        return f"{self.source_ip} -> {self.destination_ip or 'N/A'} [{self.payload_type}] - {self.classification}"

