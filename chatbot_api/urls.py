from django.contrib import admin
from django.urls import path, include
from chatbot.views import KnowledgeBaseAPIView
from django.http import JsonResponse

def debug_urls(request):
    """Endpoint temporal para debugging de URLs"""
    from django.urls import get_resolver
    resolver = get_resolver()
    
    def get_url_patterns(patterns, prefix=''):
        urls = []
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                urls.extend(get_url_patterns(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                urls.append(prefix + str(pattern.pattern))
        return urls
    
    all_urls = get_url_patterns(resolver.url_patterns)
    return JsonResponse({'urls': all_urls})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.urls')),  # Con prefijo /api/
    path('', include('chatbot.urls')),      # Sin prefijo (acceso directo)
    path("knowledge-base/", KnowledgeBaseAPIView.as_view()),
    path("knowledge-base/<int:entry_id>/", KnowledgeBaseAPIView.as_view()),
    path('debug-urls/', debug_urls),  # Endpoint temporal para debugging
]
