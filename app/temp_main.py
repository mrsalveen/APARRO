"""
This module demonstrates different functionalities of the restaurant order processing system.
It includes demonstrations of order transcription, order prediction, and direct order processing.
"""

import waiter as wt
import transcriber as tr

def main_transcribe():
    """
    Demonstrates the transcription of an order using the transcriber.
    """
    transcriber = tr.Transcriber(model_name="medium.en", device_type="cuda")
    order = transcriber.transcribe()
    print(order)

def main_predict_order():
    """
    Demonstrates the prediction and processing of an order string using the waiter.
    """
    order_str = """
    I would like to order a McCrispy without pickle and 5 large french fries. Change 2 of the 
    french fries to 2 Big Macs and add a Coke. Also add one Chicken Biriani.
    """
    waiter = wt.Waiter()
    waiter.create_order(order_str)
    waiter.print_order()

if __name__ == "__main__":
    # Uncomment the function you wish to demonstrate
    main_transcribe()
    #main_predict_order()
    # main_output_demo()
