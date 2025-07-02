from django.contrib import admin
from django.urls import path, include
from chatbot.views import KnowledgeBaseAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.urls')),
    path("knowledge-base/", KnowledgeBaseAPIView.as_view()),
    path("knowledge-base/<int:entry_id>/", KnowledgeBaseAPIView.as_view())
]
