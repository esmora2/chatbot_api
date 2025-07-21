#!/usr/bin/env python3
import requests
import json

def test_single_question():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    pregunta = "donde esta el departamento de computacion"
    
    data = {
        "message": pregunta
    }
    
    print(f"🔍 Probando: {pregunta}")
    print(f"📡 URL: {url}")
    print(f"📦 Datos: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Respuesta: {response.json()}")
        
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT después de 30 segundos")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_single_question()
