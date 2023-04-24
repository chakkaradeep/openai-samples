# openai-samples
I am exploring the possibilities of OpenAI and what we can build with it. This repository has sample scripts or apps that I am using to learn OpenAI and other AI topics.

## Q&A chat with your PDFs
With LLMs being highly proficient in inferring tasks based on given contexts, it has become feasible to provide your data as context to the model and obtain responses to queries based on that context. Essentially, ChatGPT performs this function. In this example, we offer PDF content as context to the model for a specific query, allowing it to generate a response. To accomplish this, follow these steps:
- Generate [OpenAI embeddings](https://platform.openai.com/docs/guides/embeddings) for the PDF files.
    - To generate embeddings, we [divide the PDF content into smaller segments](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/pdf.html) and subsequently create embeddings for each segment. This approach enables us to efficiently manage and process large PDF documents.
- Store the embeddings in a [Chroma](https://www.trychroma.com/) [vector database](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/chroma.html).
- Conduct a similarity search on the vector database using the query to retrieve pertinent embeddings.
- Create an [LLM chain to perform a retrieval search on PDF contents](https://python.langchain.com/en/latest/modules/chains/index_examples/vector_db_qa.html).

Additionally, this example produces PDF summaries, which are valuable in determining relevant questions to pose to the chatbot.

The demo uses [Langchain](https://python.langchain.com/en/latest/index.html) to coordinate various tasks, such as generating PDF summaries, creating embeddings, storing and loading embeddings in a vector store, and executing query retrieval from your PDF documents.

Here is the demo:


https://user-images.githubusercontent.com/7882052/234067096-51220921-7808-42e3-b97a-468d45b8a8d9.mp4



## Using Agents and Tools
LLMs are great, but they lack certain information. There is no continuous learning. So, when you ask the LLM about current events, or even as simple as 'today's date', they cannot help you. However, in some instances, if you give them the context, like *'today's date is April 18th, 2023'*, they might be helpful or provide access to other tools to seek answers, they might be helpful. [Langchain](https://python.langchain.com/en/latest/index.html)'s [Agent](https://python.langchain.com/en/latest/modules/agents.html) and [Tools](https://python.langchain.com/en/latest/modules/agents/tools.html) help you exactly with that. 

In this sample, we use a tool available in langchain library called SerpApi that searches internet and a custom tool that parses date from strings. The DateParser tool calls OpenAI, but this time with the date context. We provide the context of today's date which helps the model to answer further questions on date. 

```python
class DateParserTool(BaseTool):
    """
    Custom Tool by subclassing the BaseTool class.
    DateParserTool constructs another OpenAI call with the date context.
    This is a great example of how you can inject context into OpenAI through chaining.
    """
    name = 'Date Parser'
    description = 'Useful to infer dates from natural language strings.'

    def _run(self, tool_input: str) -> str:
        prompt_template = 'Today is {date_today}. Answer the following in Long Date format: {input}'
        prompt = PromptTemplate(template=prompt_template, input_variables=['date_today', 'input'])
        date_today = date.today()
        llm_chain = LLMChain(prompt=prompt,
                             llm=OpenAI(temperature=0.3, max_tokens=100),
                             verbose=True)
        return llm_chain.run(date_today=date_today.today(),
                             input=tool_input)

    async def _arun(self, tool_input: str) -> str:
        raise NotImplementedError('DateParser does not support async')
```

So, now if we query OpenAI with a prompt:

```
Charlie bought his phone today. His phone will be out of warranty in a month. Reply when the warranty expires along with a Hollywood movie name releasing on that day.
```
The Agent will do the following:
1. It needs to know about *'a month from today'* by using the custom DateParser tool.
2. Once *'a month from today'* is known, it now needs to know *'hollywood movies releasing in a month'* by using the SerpApi Search tool.
4. Once '*'a month from today'*' and *'hollywood movies releasing in a month'* is known, it can now construct the final answer.

```
The warranty for Charlie's phone expires on May 18, 2023 and a Hollywood movie releasing on that day is The Little Mermaid.
```

Here is the demo:

https://user-images.githubusercontent.com/7882052/232971654-7260a727-1f3b-4edd-b52f-9923394aa506.mp4



## Conversation Bot
This is a sample bot that uses [Langchain](https://python.langchain.com/en/latest/index.html) to construct the [prompt template](https://python.langchain.com/en/latest/modules/prompts/prompt_templates/getting_started.html), an [LLM chain](https://python.langchain.com/en/latest/modules/chains/getting_started.html), and [memory](https://python.langchain.com/en/latest/modules/memory/getting_started.html) to store the history. The sample uses [ConversationBufferMemory](https://python.langchain.com/en/latest/modules/memory/types/buffer.html) which allows for storing of messages in memory and then extracts the messages in a variable. Since we utilize a history, the bot is able to remember the messages and respond appropriately. You will type *exit* to exit the bot and you will have an option to save the entire conversation history.

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
