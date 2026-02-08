from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MediaType(models.TextChoices):
    TEXT = 'text', 'Text'
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Video'
    AUDIO = 'audio', 'Audio'


class MediaAnalysis(models.Model):
    """Model for storing media analysis requests and results"""
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    file = models.FileField(upload_to='media_uploads/%Y/%m/%d/', null=True, blank=True, help_text="Uploaded file")
    text_content = models.TextField(blank=True, help_text="Text content if media_type is text")
    file_url = models.URLField(blank=True, help_text="URL to media file if provided instead of upload")
    
    # Analysis Results
    what_received = models.TextField(blank=True, help_text="Description of what was received")
    what_did = models.TextField(blank=True, help_text="What the system did/analyzed")
    what_to_do_next = models.TextField(blank=True, help_text="Recommended next steps")
    
    # AI Analysis
    ai_analysis = models.TextField(blank=True, help_text="Full AI analysis response")
    risk_score = models.FloatField(null=True, blank=True, help_text="Risk score 0-100")
    is_threat = models.BooleanField(default=False, help_text="Whether this is identified as a threat")
    threat_details = models.JSONField(default=dict, blank=True, help_text="Detailed threat information")
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_analyses', null=True, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default='pending', help_text="pending, analyzing, completed, error")
    error_message = models.TextField(blank=True, help_text="Error message if analysis failed")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Media Analyses'
    
    def __str__(self):
        return f"{self.get_media_type_display()} - {self.user or 'Anonymous'} - {self.status}"


