# calculator/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time
import requests
from concurrent import futures

MAIN_SERVICE_URL = "http://localhost:8085/API/synthesis/{}/update-result/"
TOKEN = "secret123token"

executor = futures.ThreadPoolExecutor(max_workers=1)

def calculate_volume_rm(data):
    """Расчёт volume_rm по формуле с задержкой"""
    time.sleep(5)  # Задержка 5 секунд
    
    try:
        purity = float(data['purity'])
        volume_sm = float(data['volume_sm'])
        density_sm = float(data['density_sm'])
        molar_mass_sm = float(data['molar_mass_sm'])
        density_rm = float(data['density_rm'])
        molar_mass_rm = float(data['molar_mass_rm'])
        count = float(data['count'])
        
        result = ((purity * volume_sm * density_sm * molar_mass_rm) / 
                 (density_rm * molar_mass_sm)) * count
    except (KeyError, ZeroDivisionError):
        result = 0
    
    return {
        'reaction_id': data['reaction_id'],
        'volume_rm': result
    }

def process_synthesis(data):
    """Обработка всего синтеза"""
    synthesis_id = data['synthesis_id']
    reactions_data = data['data']
    
    results = []
    for reaction_data in reactions_data:
        result = calculate_volume_rm(reaction_data)
        results.append(result)
    
    return {
        'synthesis_id': synthesis_id,
        'results': results
    }

def send_results_to_main_service(task):
    """Колбэк для отправки результатов"""
    try:
        result = task.result()
    except:
        return
    
    synthesis_id = result['synthesis_id']
    results = result['results']
    
    url = MAIN_SERVICE_URL.format(synthesis_id)
    payload = {
        'token': TOKEN,
        'results': results
    }
    
    try:
        requests.put(url, json=payload, timeout=10)
    except:
        pass  # Игнорируем ошибки

@api_view(['POST'])
def calculate(request):
    """Принимает данные для расчёта"""
    if 'synthesis_id' not in request.data or 'data' not in request.data:
        return Response({'error': 'Missing data'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    task = executor.submit(process_synthesis, request.data)
    task.add_done_callback(send_results_to_main_service)
    
    return Response({
        'status': 'calculation_started',
        'synthesis_id': request.data['synthesis_id']
    }, status=status.HTTP_200_OK)