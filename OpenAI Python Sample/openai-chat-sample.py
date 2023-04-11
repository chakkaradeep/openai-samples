import openai
import configparser
import asyncio
import aiohttp
import json
import sys

# Load API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('API_KEYS', 'OPENAI-API_KEY')

# Define custom APIError exception
class APIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

# Get user input and process it
def get_user_input():
    while True:
        user_input = input(f"\nYour message: ")
        if user_input.lower() == 'exit':
            break
        else:
            status_code = run_async(process_input(user_input))
            if status_code is not None:
                break

# Run async function synchronously
def run_async(coroutine_object):
    return asyncio.get_event_loop().run_until_complete(coroutine_object)

# Process user input and display response or error message
async def process_input(user_input):
    sys.stdout.write(".....waiting for magic.....")
    sys.stdout.flush()
    try:
        response = await generate_response(user_input)
        sys.stdout.write("\r" + " " * len(".....waiting for magic.....") + "\r")
        sys.stdout.flush()
        print(response, "\n")
        return None
    except APIError as e:
        sys.stdout.write("\r" + " " * len(".....waiting for magic.....") + "\r")
        sys.stdout.flush()
        print(f"Error occurred: {e.message}")
        return e.status_code

# Call OpenAI API to generate a response
async def generate_response(user_input):
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "text-davinci-003",
            "prompt": f"{user_input}\n",
            "max_tokens": 50,
            "temperature": 0.5
        }
        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json"
        }
        async with session.post('https://api.openai.com/v1/completions',
                                data=json.dumps(payload),
                                headers=headers) as resp:
            result = await resp.json()
            if resp.status == 200:
                return result['choices'][0]['text'].strip()
            else:
                raise APIError(resp.status, result.get('error', 'Unknown error'))

# Main function to start the app
def main():
    print(f"\nWelcome to the ChatGPT Python app!")
    get_user_input()
    print(f"\nExiting the app. Have a great day!\n")

# Entry point of the script
if __name__ == '__main__':
    main()
