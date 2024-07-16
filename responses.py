from random import choice
import utils
import os
import dotenv

dotenv.load_dotenv()

def get_response(user_input: str) -> list:
    lowered: str = user_input.lower().strip()
    if lowered ==  "":
        return ["You didn't say anything! :'("]
    elif "hello" in lowered:
        return [choice(["Hello!", "Hi!", "Hey there!", "Greetings!", "Salutations!", "Hello, friend!", "Hello, world!"])]
    elif lowered.startswith("r "):
        try:
            return [utils.handle_roll_command(lowered)]
        except Exception as e:
            return [utils.format_embed_message_of_error(e)]
        
    elif lowered.startswith("rs "):
        try:
            return utils.handle_roll_stats_command(lowered)
        except Exception as e:
            return utils.format_embed_message_of_error(e)
    elif lowered.startswith("e "):
        try:
            return utils.handle_expected_value_command(lowered)
        except Exception as e:
            return utils.format_embed_message_of_error(e)
    else:
        return [choice(["I'm sorry, I don't understand.", "I'm not sure what you mean.", "try rephrasing that.",
                         "I'm not sure what you're asking for.", "Error 404 - response not found beep boop."])]
