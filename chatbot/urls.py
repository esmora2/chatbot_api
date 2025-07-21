from django.urls import path
from .views import ChatbotAPIView, ChatbotTestContextAPIView
from .simple_views import FAQManagementAPIView, FAQDuplicateCheckAPIView, SimpleTestAPIView
from .firebase_views import FirebaseFAQManagementAPIView, FirebaseFAQSearchAPIView, FirebaseStatusAPIView
from django.http import JsonResponse
from django.views import View
from .document_loader import cargar_documentos

class TestView(View):
    def get(self, request):
        return JsonResponse({'message': 'Test endpoint working', 'method': 'GET'})
    
    def post(self, request):
        return JsonResponse({'message': 'Test endpoint working', 'method': 'POST'})

class DocumentCheckView(View):
    def get(self, request):
        """
        Endpoint simple para verificar documentos cargados
        """
        try:
            documentos = cargar_documentos()
            
            # Contar por tipo
            stats = {"total": len(documentos), "faq": 0, "web": 0, "pdf": 0, "pdfs": {}}
            
            for doc in documentos:
                source = doc.metadata.get("source", "unknown")
                if source in ["faq", "web", "pdf"]:
                    stats[source] += 1
                
                if source == "pdf":
                    filename = doc.metadata.get("filename", "unknown")
                    if filename not in stats["pdfs"]:
                        stats["pdfs"][filename] = 0
                    stats["pdfs"][filename] += 1
            
            # Verificar PDF específico
            pdf_target = "espe_software_aplicaciones_basadas_en_el_conocimiento.pdf"
            pdf_chunks = stats["pdfs"].get(pdf_target, 0)
            
            return JsonResponse({
                "documentos_totales": stats["total"],
                "faq_count": stats["faq"],
                "web_count": stats["web"],
                "pdf_count": stats["pdf"],
                "pdfs_detectados": list(stats["pdfs"].keys()),
                "pdf_especifico": {
                    "nombre": pdf_target,
                    "chunks": pdf_chunks,
                    "encontrado": pdf_chunks > 0
                }
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('docs/check/', DocumentCheckView.as_view(), name='document-check'),
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('chatbot/test-context/', ChatbotTestContextAPIView.as_view(), name='chatbot-test-context'),
    
    # Endpoints CSV originales (mantenidos por compatibilidad)
    path('faq/manage/', FAQManagementAPIView.as_view(), name='faq-management'),
    path('faq/check-duplicate/', FAQDuplicateCheckAPIView.as_view(), name='faq-duplicate-check'),
    
    # Nuevos endpoints Firebase
    path('firebase/faq/', FirebaseFAQManagementAPIView.as_view(), name='firebase-faq-management'),
    path('firebase/faq-management/', FirebaseFAQManagementAPIView.as_view(), name='firebase-faq-management-post'),
    path('firebase/search/', FirebaseFAQSearchAPIView.as_view(), name='firebase-faq-search'),
    path('firebase/status/', FirebaseStatusAPIView.as_view(), name='firebase-status'),
]
