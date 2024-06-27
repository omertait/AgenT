
class Task:
    '''
    Define a task for execution.
    The task is done by the agent.
    The task is defined by a function.
    The function should accept two arguments: result and memory.
    The result is the output of the previous task.
    The memory is the memory of the agent.
    the function should return a list of steps.
    Each step is a dictionary that contains some fields.
    The type field is mandatory.
    the types defined in the toolsFactory.py file.
    '''

    def __init__(self, agent, function):
        self.agent = agent
        self.function = function

    def assignAgent(self, agent):
        self.agent = agent
        return self

    def execute(self, result, memory):
        steps = self.function(result, memory)
        response = self.agent.execute(steps=steps)
        return response
    
    