# Documentation:
'''
This file contains the step handlers for the task

A task can have multiple steps.
the types of the steps are defined here.
Each step type has a corresponding function that handles it.

Validation:
A step is a dictionary.
the step has to have the necessary fields according to the step type.

mandatory fields:
- type: str - the type of the step 

update_memory step:
- update_memory_func: function that updates the memory
- memory_arg: any

tool step:
- tool: str - the name of the tool
- input_data_func: function that returns the input data for the tool

llm_interact step:
- messages: function that returns the messages for the llm 
    --  arguments:
        - last_step_result: str - the result of the last step 
          each step executed one after the other, 
          the result of the previous step is the input for the next step.
          **if the step is the first one, use the task function's argument - task_input instead**
- model: str - the model to use for the llm 
(default is "gpt-4o-mini", defined in the handle_llm_interact)

'''
from enum import Enum
import ast

class StepType(Enum):
    UPDATE_MEMORY = "update_memory"
    TOOL = "tool"
    LLM_INTERACT = "llm_interact"

class StepHandler:
    def __init__(self):

        # Dictionary mapping step types to their corresponding functions
        self.step_handlers = {
            StepType.UPDATE_MEMORY.value: lambda agent_instance, step, response: handle_update_memory(agent_instance, step, response),
            StepType.TOOL.value: lambda agent_instance, step, response: handle_tool(agent_instance, step, response),
            StepType.LLM_INTERACT.value: lambda agent_instance, step, response: handle_llm_interact(agent_instance, step, response),
        }
        
        self.step_builders = {
            StepType.UPDATE_MEMORY.value: build_update_memory,
            StepType.TOOL.value: build_tool,
            StepType.LLM_INTERACT.value: build_llm_interact,
        }

    
    def get(self, step_type):
        return self.step_handlers.get(step_type)

    def build(self, step, task_input, memory):
        return self.step_builders.get(step["type"])(step=step, task_input=task_input, memory=memory)


# steps handling functions

def handle_llm_interact(agent_instance, step, response):
    messages = [
        {"role": "system", "content": agent_instance.role},
    ]
    step_messages = step["messages"](response)
    messages.extend(step_messages)

    response = agent_instance.interact_func(
        llm_client=agent_instance.llm_client,
        messages=messages, 
        model=step.get("model", "gpt-4o-mini"))
    
    return response
    
def handle_tool(agent_instance, step, response):
    return agent_instance.tools[step["tool"]][0](**step["input_data_func"](response))

def handle_update_memory(agent_instance, step, response):
    return step["update_memory_func"](response, step["memory_arg"])


def validate(function):
        '''
        validate the structure of the task
        '''
        if not callable(function):
            raise Exception("function should be a function")
        
        steps = function(None, None)
        if not isinstance(steps, list):
            raise Exception("function should return a list of steps")
        for step in steps:
            validateSteps(step)
        return True
    
def validateSteps(step) -> bool:
        ''' 
        check the structure of the step
        if is not valid - raise an exception
        '''
        if not isinstance(step, dict):
            raise Exception("step should be a dictionary")
        if "type" not in step:
            raise Exception("step should have a type")
        if step["type"] == StepType.LLM_INTERACT.value:
            if "messages" not in step:
                raise Exception("llm_interact step should have a messages function")
        elif step["type"] == StepType.TOOL.value:
            if "tool" not in step:
                raise Exception("tool step should have a tool name")
            if "input_data_func" not in step:
                raise Exception("tool step should have an input_data_func function")
        elif step["type"] == StepType.UPDATE_MEMORY.value:
            if "update_memory_func" not in step:
                raise Exception("update_memory step should have an update_memory_func function")
            if "memory_arg" not in step:
                raise Exception("update_memory step should have a memory_arg")
        else:
            raise Exception(f"step type not recognized: {step['type']}")
        return True

# builders
def build_llm_interact(step, task_input, memory):
    promptTemplate = step["promptTemplate"]
    model = step.get("model", "gpt-3.5-turbo")

    def messages_func(last_step_result):
        messages = [
                    {"role": "user", "content": promptTemplate.format(memory=memory, task_input=task_input, last_step_result=last_step_result)},
                ]
        return messages
    return {"type" : StepType.LLM_INTERACT.value, "messages" : messages_func, "model": model}

def build_tool(step, task_input, memory):
    tool_name = step["tool"]
    input_data_func_expression = step["input_data_func"]
    tree = ast.parse(input_data_func_expression, mode='eval')
    # need to implement a safe eval
    code = compile(tree, '<string>', 'eval')
    return {"type" : StepType.TOOL.value, "tool": tool_name, "input_data_func": lambda last_step_result: eval(code, {'last_step_result': last_step_result})}

def build_update_memory(step, task_input, memory):
    # memory, memory_arg_input
    memory_arg_input = step["memory_arg"]
    
    def update_memory_func(last_step_result, memory_arg):
        memory[memory_arg] = last_step_result
        return last_step_result
    
    return {"type" : StepType.UPDATE_MEMORY.value, "update_memory_func": update_memory_func, "memory_arg": memory_arg_input}
