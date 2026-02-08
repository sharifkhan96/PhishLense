from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ThreatViewSet, api_root
from .traffic_views import TrafficEventViewSet
from .media_views import MediaAnalysisViewSet
from .auth_views import RegisterView, login_view, current_user_view

router = DefaultRouter()
router.register(r'threats', ThreatViewSet, basename='threat')
router.register(r'traffic', TrafficEventViewSet, basename='traffic')
router.register(r'media', MediaAnalysisViewSet, basename='media')

urlpatterns = [
    # API root (public)
    path('', api_root, name='api_root'),
    
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/me/', current_user_view, name='current_user'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes
    path('', include(router.urls)),
]

