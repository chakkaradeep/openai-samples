# openai-samples
I am exploring the possibilities of OpenAI and what we can build with it. This repository has sample scripts or apps that I am using to learn OpenAI and other AI topics.

## Conversation Bot
This is a sample bot that uses [Langchain](https://python.langchain.com/en/latest/index.html) to construct the prompt, an LLM chain, and an in-memory buffer to store the history. The sample uses [ConversationBufferMemory](https://python.langchain.com/en/latest/modules/memory/types/buffer.html) which allows for storing of messages and then extracts the messages in a variable. Since we utilize a history, the bot is able to remember the messages and respond appropriately. You will type *exit* to exit the bot and you will have an option to save the entire conversation history.

Here is the demo:

https://user-images.githubusercontent.com/7882052/231362453-63237702-1cd2-4b9f-9222-907a78f29e64.mp4

## Question answering over docs
The simple python script uses [Langchain](https://python.langchain.com/en/latest/index.html), loads a text file, creates indexes (from OpenAI embeddings) and then allows you to [ask questions on your document data](https://python.langchain.com/en/latest/use_cases/question_answering.html). For this sample, I am using my Kindle Highlights file which you can find in your Kindle. I am using [Chroma storage](https://www.trychroma.com/) to persist the embeddings once created. 

Here is the demo:

https://user-images.githubusercontent.com/7882052/230826093-eaee1fcc-36bb-4a9d-91dc-17e1fea0a060.mp4

## OpenAI Python Sample
This is beginner sample on how to interact with OpenAI APIs, specifically the [Completions API](https://platform.openai.com/docs/api-reference/completions). It builds a simple python chat bot but does not retain or remember conversation history. You will type *exit* to exit the bot.

The sample was **built from scratch using ChatGPT (GPT4)**. 
You can view the entire [conversation here](https://github.com/chakkaradeep/openai-samples/blob/f255c95df4fef1cec228d64fa920a45f596608b3/OpenAI%20Python%20Sample/gpt4_chat_build_python_sample.md). This is a good example on how you can use [chain of thought prompting](https://learnprompting.org/docs/intermediate/chain_of_thought) so it can help you build great apps.

Here is the demo: 

https://user-images.githubusercontent.com/7882052/231063129-8f32dca8-bd93-4a8e-a68e-acbc1f5b152e.mp4
