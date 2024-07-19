


import time


class Agent:
    '''
    Agent class
    name: str - the name of the agent ** just for reference **
    llm_client: client instance for the llm
    interact_func: function that interacts with the llm
    role: str - the role of the agent ** system prompt **
    step_handler: StepHandler instance for handling the steps
    tools: dict - dictionary of tools available to the agent
    '''
    
    def __init__(self, name, llm_client, interact_func, role, step_handler):
        self.name = name
        self.llm_client = llm_client
        self.tools = {}
        self.interact_func = interact_func
        self.role = role
        self.step_handler = step_handler


    def add_tool(self, tool_name, tool_info):
        self.tools[tool_name] = tool_info # tool_info: [toolFunction, toolDescription]
    

    def execute(self, steps):
        '''
        function: function that returns the messages list for the llm
        model: str - the model to use for the llm (as the agent can use 
                                different models for different tasks)
        '''

        # last_step_response: the response of the last step
        # Task's input is already embedded in the first step
        
        last_step_response = None
        for step in steps:
            handler = self.step_handler.get(step["type"])
            if handler:
                # start time
                start_time = time.time()
                last_step_response = handler(self, step, last_step_response)
                # end time
                end_time = time.time()
                print(f"step {step['type']} executed in {end_time - start_time} seconds.")
                print(f"step {step['type']} executed successfully.\nResult:\n{last_step_response}\n---------------------------------\n")
        return last_step_response
    
    

