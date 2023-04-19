import configparser
import os
from datetime import date
from typing import List
from langchain import OpenAI, SerpAPIWrapper, PromptTemplate, LLMChain
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.tools import BaseTool


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


def get_tools() -> List[BaseTool]:
    """
    Set up and return the tools
    :return: a list of tools
    """
    search = SerpAPIWrapper()
    date_parser_tool = DateParserTool()

    # We load two tools. Our DateParser and a SerpApi search tool
    tools: List[BaseTool] = [
        date_parser_tool,
        Tool(name='Search', description='Useful if you want to search internet.', func=search.run)
    ]
    return tools


def execute_agent():
    """
    Initialize and execute the agent
    """
    llm = OpenAI(temperature=0.3, max_tokens=200)
    agent = initialize_agent(get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    agent.run('Charlie bought his phone today. His phone will be out of warranty in a month. Reply when the warranty '
              'expires along with a Hollywood movie name releasing on that day.')


def initialize() -> None:
    """
    Load the config file and set the OpenAI and SerpApi API key.
    Get your SerpApi key here: https://serpapi.com/
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    os.environ['OPENAI_API_KEY'] = config.get('API_KEYS', 'OPENAI_API_KEY')
    os.environ['SERPAPI_API_KEY'] = config.get('API_KEYS', 'SERPAPI_API_KEY')


if __name__ == '__main__':
    initialize()
    execute_agent()
