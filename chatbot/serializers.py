from rest_framework import serializers


class FAQEntrySerializer(serializers.Serializer):
    """
    Serializer para validar entradas de FAQ
    """
    pregunta = serializers.CharField(
        max_length=500,
        help_text="La pregunta que se va a agregar al FAQ"
    )
    respuesta = serializers.CharField(
        max_length=2000,
        help_text="La respuesta correspondiente a la pregunta"
    )
    
    def validate_pregunta(self, value):
        """
        Valida que la pregunta no esté vacía y tenga un formato adecuado
        """
        if not value.strip():
            raise serializers.ValidationError("La pregunta no puede estar vacía")
        
        if len(value.strip()) < 5:
            raise serializers.ValidationError("La pregunta debe tener al menos 5 caracteres")
            
        return value.strip()
    
    def validate_respuesta(self, value):
        """
        Valida que la respuesta no esté vacía y tenga un formato adecuado
        """
        if not value.strip():
            raise serializers.ValidationError("La respuesta no puede estar vacía")
        
        if len(value.strip()) < 10:
            raise serializers.ValidationError("La respuesta debe tener al menos 10 caracteres")
            
        return value.strip()


class ChatbotQuerySerializer(serializers.Serializer):
    """
    Serializer para validar consultas al chatbot
    """
    pregunta = serializers.CharField(
        max_length=500,
        help_text="La pregunta para el chatbot"
    )
    
    def validate_pregunta(self, value):
        if not value.strip():
            raise serializers.ValidationError("La pregunta no puede estar vacía")
        return value.strip()
