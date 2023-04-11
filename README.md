# openai-samples
I am exploring the possibilities of OpenAI and what we can build with it. This repository has sample scripts or apps that I am using to learn OpenAI and other AI topics.

## OpenAI Python Sample
This is beginner sample on how to interact with OpenAI APIs, specifically the [Completions API](https://platform.openai.com/docs/api-reference/completions). It builds a simple python chat bot but does not retain or remember conversation history. 

The sample was built usig ChatGPT (GPT4) and you can view the entire conversation here. This is a good example on how you can use [chain of thought prompting](https://learnprompting.org/docs/intermediate/chain_of_thought) so it can help you build great apps.

Here is the demo: 


## Question answering over docs
The simple python script uses [Langchain](https://python.langchain.com/en/latest/index.html), loads a text file, creates indexes (from OpenAI embeddings) and then allows you to [ask questions on your document data](https://python.langchain.com/en/latest/use_cases/question_answering.html). For this sample, I am using my Kindle Highlights file which you can find in your Kindle. I am using [Chroma storage](https://www.trychroma.com/) to persist the embeddings once created. 

Here is the demo:

https://user-images.githubusercontent.com/7882052/230826093-eaee1fcc-36bb-4a9d-91dc-17e1fea0a060.mp4