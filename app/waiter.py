"""
This module contains the Waiter class which is responsible for processing customer orders.
It uses a language model to interpret the orders and matches them against a menu.
"""

import json
import logging
import textwrap

from ctransformers import AutoConfig, AutoModelForCausalLM
from thefuzz import process
import menu as mn

MODEL_PATH = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
MODEL_FILE = "mistral-7b-instruct-v0.1.Q5_K_M.gguf"
MODEL_TYPE = "mistral"
INITIAL_PROMPT = textwrap.dedent("""
    Welcome to our restaurant order processing service. Before proceeding, please ensure that you spend some time analyzing the customer's order carefully. Customers may provide complex orders with modifications, and it's important to accurately interpret their preferences.
    Please provide the customer's order in a clear and structured manner. We will assist you in converting it to JSON format for easy processing. Follow the instructions below:
    1. Spend time to thoroughly analyze what the customer has ordered. Customers may provide detailed requests, such as modifying their initial order, which requires your attention to ensure their order is processed accurately. Also make sure to include sizes of dishes/drinks in the comments. If the customer DID NOT MENTION the order or any food items, return an EMPTY json file
    2. Provide the following information for each item:
    - Dish: The name of the dish.
    - Quantity: The number of portions or items ordered.
    - Comment: Any specific instructions or comments related to the order (including size of the drink like: large, medium, small, and other comments like cold, hot, spicy).
    3. Format the order as a JSON object with the following keys:
    {{
        "dish": "Dish Name",
        "quantity": 2,  # Adjust the quantity as needed
        "comment": "Add extra cheese"
    }}
    Now please find the order below inside backtics and return order in the proper JSON format
""")
logging.basicConfig(level=logging.INFO)

class Waiter:
    """
    The Waiter class processes customer orders by interpreting them with a large language model
    and matching them against a known menu. It handles both available and unavailable items.
    """
    def __init__(self):
        self._ordered = []
        self._unavailable = []
        self._llm = initialize_model(MODEL_PATH, MODEL_FILE, MODEL_TYPE)

    def _process_order(self, order: dict):
        """
        Processes a customer's order, confirming items and identifying those not on the menu.

        Args:
        order (dict): The customer's order as a dictionary.

        Updates:
        self._ordered (list of dictionaries): List of dictionaries 
        containing keys as "dish", "quantity", and "comment".
        self._unavailable (list of dishes): List of dishes (names) not found in the menu.
        """
        for food_item in order:
            dish = food_item["dish"]
            quantity = food_item["quantity"]
            try:
                comment = food_item["comment"]
            except KeyError:
                comment = ""
            # Using fuzziness to find the most similar item on the menu
            best_match, similarity_score = process.extractOne(dish, mn.mcdonalds_menu)
            # Make sure this item does belong in the menu,
            # if similarity is below 90 - it is not in menu
            if similarity_score >= 90:
                confirmed_item = {"dish": best_match, "comment": comment, "quantity": quantity}
                self._ordered.append(confirmed_item)
            else:
                self._unavailable.append(dish)

    def create_order(self, order: str):
        """
        Processes a customer's order and returns a confirmed order and items not on the menu.

        Args:
        order (str): The customer's order as a string.

        Returns:
        tuple: A tuple containing two lists - ordered and ordered_not_in_menu.
        """
        # Stage 1, Creating Prompt for the Model
        prompt = create_prompt(order)
        # Stage 2, Running the model
        logging.info("Predicting...")
        json_order = self._llm(prompt, max_new_tokens=2048, temperature=0.0,
                         top_k=55, top_p=0.9, repetition_penalty=1.2)
        logging.info("Model output: %s", json_order)
        # Stage 3, Converting from JSON to dictionary
        dict_order = json_to_dict(json_order)
        # Stage 4, Processing the Order
        self._process_order(dict_order)

    def print_order(self):
        """
        Prints the ordered items and unavailable items in a formatted manner.

        Args:
        ordered (list): List of ordered items (as dictionaries 
        with keys "dish", "comment", and "quantity").
        unavailable (list): List of unavailable items.
        """
        ordered_items = []
        unavailable_items = self._unavailable
        for item in self._ordered:
            ordered_item_str = f"{item['quantity']} {item['dish']}"
            if item['comment']:
                ordered_item_str += f" ({item['comment']})"
            ordered_items.append(ordered_item_str)
        ordered_str = ", ".join(ordered_items)
        unavailable_str = ", ".join(self._unavailable)
        result_str = ""
        if ordered_items:
            result_str += f"{ordered_str}\n"
        else:
            result_str += "Sorry, there is nothing in our menu which you ordered\n"
        if unavailable_items:
            result_str += f"Unfortunately we don't have: {unavailable_str}\n"
        return result_str


def create_prompt(order: str, initial_prompt=INITIAL_PROMPT):
    """
    Creates a prompt for the model to process a customer's order.

    Args:
    order (str): The customer's order as a string.

    Returns:
    str: The prompt for the model including the order.
    """
    prompt = textwrap.dedent(f"""
    {initial_prompt}
    ```{order}```
    JSON:
    """)
    return prompt.strip()

def initialize_model(model_path_or_repo_id, model_file, model_type):
    """
    Initializes an LLM from AutoModelForCausalLM.

    Returns:
    AutoModelForCausalLM: The initialized large language model.
    """
    try:
        config = AutoConfig.from_pretrained("TheBloke/Mistral-7B-v0.1-GGUF")
        config.config.max_new_tokens = 2560
        config.config.context_length = 4096
        return AutoModelForCausalLM.from_pretrained(model_path_or_repo_id,
                                                    model_file=model_file,
                                                    model_type=model_type,
                                                    config=config)
    except Exception as e:
        raise RuntimeError("Error initializing the model: " + str(e)) from e

def json_to_dict(json_str: str):
    """
    Converts a JSON string to a Python dictionary.

    Args:
    json_str (str): The JSON string to convert.

    Returns:
    dict: The Python dictionary representation of the JSON.
    """
    try:
        json_str = json_str.strip()
        json_str = '[' + json_str + ']'
        json_dict = json.loads(json_str)
        return json_dict
    except Exception as e:
        raise RuntimeError("Error converting JSON to dictionary: " + str(e)) from e
