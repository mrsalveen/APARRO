from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import sys
sys.path.append('../app')
from restaurant import Restaurant as rst
from transcriber import Transcriber

tr = Transcriber(model_name="medium.en", device_type="cuda")

@csrf_exempt
def take_order(request):
    if request.method == 'POST':
        # Handle the audio file sent from the frontend
        audio_file = request.FILES.get('audio_data')

        # Create the restaurant object
        restaurant = (
            rst.builder()
            .with_transcriber(model_name="medium.en", device_type="cuda")
            .with_waiter()
            .build()
        )

        # Use the transcriber to get the order text
        order_text = restaurant._transcriber._transcribe_audio(audio_file)
        # Process the order
        order_res = restaurant._waiter.create_order(order_text)
        order_result = restaurant._waiter.print_order()

        return JsonResponse({'order': order_result})
    return render(request, 'take_order.html')

@csrf_exempt
def pause_recording(request):
    if request.method == 'POST':
        # Call pause method on your Transcriber instance
        # Assuming you have a global or accessible instance of Transcriber
        tr._pause_recording()
        return JsonResponse({'status': 'paused'})

@csrf_exempt
def resume_recording(request):
    if request.method == 'POST':
        # Call resume method on your Transcriber instance
        tr._resume_recording()
        return JsonResponse({'status': 'resumed'})


def index(request):
    return render(request, 'index.html')

def ready_page(request):
    return render(request, 'ready_page.html')