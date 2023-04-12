import os
import configparser
import asyncio
import sys
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Load API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
os.environ["OPENAI_API_KEY"] = config.get('API_KEYS', 'OPENAI-API_KEY')

prompt_template = """You are a helpful conversation Assistant.You are here to help 
keep the human entertained and provide with engaging responses. You will be friendly, respectful,
and use your profound knowledge to help the human.  

You will provide accurate responses. You do not have knowledge about current events. You should not
hallucinate and generate your own responses. In case, you are not sure about something or unable to provide 
an accurate response, you will politely say you are unable to help and ask the human on what else you can help with. 

{history}

Human: {human_input}
Assistant:"""


# Call OpenAI API to generate a response
async def generate_response(chatgpt_chain, user_input):
    response = await chatgpt_chain.arun(human_input=user_input)
    return response


# Process user input and display response or error message
async def process_input(chatgpt_chain, user_input):
    sys.stdout.write(".....waiting for magic.....")
    sys.stdout.flush()
    try:
        response = await generate_response(chatgpt_chain, user_input)
        sys.stdout.write("\r" + " " * len(".....waiting for magic.....") + "\r")
        sys.stdout.flush()
        print(response, "\n")
        return None
    except Exception as e:
        sys.stdout.write("\r" + " " * len(".....waiting for magic.....") + "\r")
        sys.stdout.flush()
        error_message = "AI Assistant encountered an error. Please try again later."
        print(error_message)
        return error_message


# Run async function synchronously
def run_async(coroutine_object):
    return asyncio.get_event_loop().run_until_complete(coroutine_object)


# Export the chat history into a text file
def export_chat_history(memory, filename):
    formatted_history = ""
    for message in memory['history']:
        if isinstance(message, HumanMessage):
            formatted_history += f"Human: {message.content}\n"
        elif isinstance(message, AIMessage):
            formatted_history += f"Assistant: {message.content}\n\n"

    # Create a new file to store the conversation history
    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, 'w') as f:
        f.write(formatted_history)
    print("Conversation history exported successfully to human_assistant_messages.txt!")


# Get user input and process it
def get_user_input(chatgpt_chain):
    while True:
        user_input = input(f"\nYour message: ")
        if user_input.lower() == 'exit':
            export_input = input(f"\nNice talking to you. Do you want to export our conversation? (Y/N): ")
            if export_input.lower() == 'y':
                # Access the memory
                memory = chatgpt_chain.memory.load_memory_variables({})
                # Save chat history in memory
                export_chat_history(memory, "human_assistant_messages.txt")
            break
        else:
            error_message = run_async(process_input(chatgpt_chain, user_input))
            if error_message is not None:
                break


# Initialize the prompt and llm chain
def initialize_chatbot():
    # Initialize the prompt
    prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=prompt_template
    )

    # Initialize the LLM Chain and memory
    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0, max_tokens=100),
        prompt=prompt,
        memory=ConversationBufferMemory(return_messages=True)
    )
    return chatgpt_chain


# Main function to start the app
def main():
    print(f"\nWelcome to the ChatGPT Chatbot app!")
    chatgpt_chain = initialize_chatbot()
    get_user_input(chatgpt_chain)
    print(f"\nExiting the app. Have a great day!\n")


# Entry point of the script
if __name__ == '__main__':
    main()
