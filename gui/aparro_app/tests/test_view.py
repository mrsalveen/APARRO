from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from aparro_app.views import take_order
from pydub import AudioSegment
import os 
import io
class TakeOrderViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # # tests a simple order
    # def test_take_simple_order(self):
    #     audio_path = os.path.join(os.path.dirname(__file__), "order.wav")
    #     with open(audio_path, 'rb') as f:
    #         audio_data = f.read()
    #     audio_buffer = io.BytesIO(audio_data)

    #     url = reverse('take_order')  # assuming 'take_order' is the name of the URL pattern
    #     request = self.factory.post(url, {'audio_data': audio_buffer})

    #     response = take_order(request)

    #     self.assertEqual(response.status_code, 200)

    #     response_data = response.content.decode('utf-8')
    #     self.assertIn('1 Big Mac, 1 Coke', response_data)
        
        
    # # Test for order which was changed. For example I want coke, actually change it to sprite
    # def test_take_order_changed(self):
    #     audio_path = os.path.join(os.path.dirname(__file__), "changed_order.mp3")
    #     with open(audio_path, 'rb') as f:
    #         audio_data = f.read()
    #     audio_buffer = io.BytesIO(audio_data)

    #     url = reverse('take_order')  # assuming 'take_order' is the name of the URL pattern
    #     request = self.factory.post(url, {'audio_data': audio_buffer})

    #     response = take_order(request)

    #     self.assertEqual(response.status_code, 200)

    #     response_data = response.content.decode('utf-8')
    #     self.assertIn('1 Mac Chicken', response_data)
        
    # Test order partially in menu
    def test_take_order_partially_in_menu(self):
        audio_path = os.path.join(os.path.dirname(__file__), "partially_in_menu_order.mp3")
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        audio_buffer = io.BytesIO(audio_data)

        url = reverse('take_order')  # assuming 'take_order' is the name of the URL pattern
        request = self.factory.post(url, {'audio_data': audio_buffer})

        response = take_order(request)

        self.assertEqual(response.status_code, 200)

        response_data = response.content.decode('utf-8')
        self.assertIn('1 Big Mac, 1 SpriteMcToast, 1 French Fries\\nUnfortunately we don\'t have: Fanta\\n', response_data)

    # # Test order not in menu
    # def test_take_order_not_in_menu(self):
    #     audio_path = os.path.join(os.path.dirname(__file__), "not_in_menu_order.mp3")
    #     with open(audio_path, 'rb') as f:
    #         audio_data = f.read()
    #     audio_buffer = io.BytesIO(audio_data)

    #     url = reverse('take_order')  # assuming 'take_order' is the name of the URL pattern
    #     request = self.factory.post(url, {'audio_data': audio_buffer})

    #     response = take_order(request)

    #     self.assertEqual(response.status_code, 200)

    #     response_data = response.content.decode('utf-8')
    #     self.assertIn('Sorry, there is nothing in our menu which you ordered\\nUnfortunately we don\'t have: Iced Tea, Chicken Biryani\\n', response_data)
        