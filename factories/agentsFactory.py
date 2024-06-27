
from buildingBlocks.agent import Agent
from factories.toolsFactory import ToolsFactory
from factories.stepHandlers import StepHandler

class AgentsFactory:
    '''
    Factory class for creating agents
    '''
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.toolsFactory = ToolsFactory()
        self.step_handler = StepHandler()

    def createAgent(
            self, 
            name, 
            interact_func, 
            role, 
            tools = None
        ):

        '''
        name: str
        interact_func: function
        role: str
        tools: list[str] - list of tool names
        '''

        agent = Agent(
            name=name, 
            llm_client=self.llm_client, 
            interact_func=interact_func, 
            role=role, 
            step_handler=self.step_handler
        )
        
        if tools is not None:
            for tool_name in tools:
                agent.add_tool(tool_name, self.toolsFactory.getTool(tool_name))
        return agent