from buildingBlocks.task import Task
from factories.stepHandlers import validate

class TaskFactory:
    '''
    Factory class for creating tasks
    '''
   
    def createTask(self, agent, function):
        '''
        function: function
        model: str
        '''
        validate(function)
        return Task(
            agent=agent, 
            function=function
        )
    
    def assignAgent(self, agent, task):
        return task.assignAgent(agent)
    

