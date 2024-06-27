
from factories.stepHandlers import StepHandler, validate


class TaskFunctionFactory:
    '''
    Factory class for creating task functions
    '''
    def __init__(self):
        self.stepHandler = StepHandler()
        
    
    def createTaskFunction(self, steps_specs):
        '''
        steps: list of dictionaries
        the factory gets a list of steps such that
        each step contains:
        - type: str - the type of the step
        - other fields that are specific to the type
        '''
        try:
            for step_spec in steps_specs:
                if not isinstance(step_spec, dict):
                    raise Exception("step should be a dictionary")
                if "type" not in step_spec:
                    raise Exception("step should have a type field")
                
            
            def func(task_input, memory):
                steps = []
                for step in steps_specs:
                    steps.append(self.stepHandler.build(step, task_input, memory))

                return steps
            
            validate(func)
            return func
        except Exception as e:
            raise e

# # usage:
# taskFunctionFact = TaskFunctionFactory()
# steps_specs = [
#     {"type" : "llm_interact", "promptTemplate" : "summarize to one sentence: {task_input}"},
#     {"type" : "tool", "tool" : "summarize", "input_data_func" : "'x' + 'omer'"},
#     {"type" : "update_memory", "memory_arg" : "key"}
# ]
# taskFunction = taskFunctionFact.createTaskFunction(steps_specs)
# memory = {}
# print(taskFunction("input", memory)[2]['update_memory_func']("response", "key"))
# print(memory)