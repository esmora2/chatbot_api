from django.urls import path
from .views import ChatbotAPIView, ChatbotTestContextAPIView
from .simple_views import FAQManagementAPIView, FAQDuplicateCheckAPIView, SimpleTestAPIView
from django.http import JsonResponse
from django.views import View

class TestView(View):
    def get(self, request):
        return JsonResponse({'message': 'Test endpoint working', 'method': 'GET'})
    
    def post(self, request):
        return JsonResponse({'message': 'Test endpoint working', 'method': 'POST'})

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('chatbot/test-context/', ChatbotTestContextAPIView.as_view(), name='chatbot-test-context'),
    path('faq/manage/', FAQManagementAPIView.as_view(), name='faq-management'),
    path('faq/check-duplicate/', FAQDuplicateCheckAPIView.as_view(), name='faq-duplicate-check'),
]
