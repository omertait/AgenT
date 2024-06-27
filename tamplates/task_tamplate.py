'''
This is a template for a task.
arguments:
    - task_input: str - the input for the task 
    (the output of the previous task or the user input)
    - memory: dict - a global memory that is shared between all the tasks 
    and can be accessed and modified by all of them.

    return:
    - steps: list of dictionaries - each dictionary represents a step.
    the step can be of different types.
    ** types are defined in stepHandlers.py **
    
'''
def task(task_input, memory):
    def messages_func(last_step_result):
        messages1 = [
                    {"role": "user", "content": f"summarize to one sentence: {task_input}"},
                ]
        return messages1
    
    
    steps = [
        {"type" : "llm_interact", "messages" : messages_func},
    ]
    return steps