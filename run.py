from buildingBlocks.flowGraph import FlowGraph
from conversationManger import ConversationManager
from factories.agentsFactory import AgentsFactory
from factories.taskFunctionFactory import TaskFunctionFactory
from factories.tasksFactory import TaskFactory
from config.settings import import_client, interact_with_agent

llm_client = import_client()


# Usage
func="""def calculator_two_numbers(x, y, operation):
    if operation == "add":  
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        return x / y
    else:
        return None"""

agentsFactory = AgentsFactory(llm_client=llm_client)
agentsFactory.toolsFactory.addTool("calculator", func, {"description": "calculates two numbers based on given operation (add/ subtract/ multiply/ divide)" ,"x": "number", "y": "number", "operation": "string"})
agent = agentsFactory.createAgent("John", interact_with_agent, "friend", tools=["calculator"])

taskFunctionFactory = TaskFunctionFactory()
task_hello_func = taskFunctionFactory.createTaskFunction([{ "type": "tool", "tool": "calculator", "input_data_func": '{"x":1, "y":2, "operation":"add"}'},
                                                          {"type" : "llm_interact", "promptTemplate" : "responed to your student and help him find the answer to his question: {task_input}\n\nact as a private tutor. you already solved the question without showing the student the answer and the answer is: {last_step_result}.", "model": "gpt-4o-mini"}])
task_summ_func = taskFunctionFactory.createTaskFunction([{"type" : "llm_interact", "promptTemplate" : "summarize to one sentence: {task_input}", "model": "gpt-4o-mini"}])

taskFactory= TaskFactory()
task = taskFactory.createTask(agent, task_hello_func)
task_summ = taskFactory.createTask(agent, task_summ_func)

flow_graph = FlowGraph()
flow_graph.add_task("start" , task)
flow_graph.add_task("summary" , task_summ)
flow_graph.set_start_node("start")
flow_graph.add_edge("start", "summary")

conversationManager = ConversationManager(flow_graph, "1")
response, run_time = conversationManager.run("what is 1 + 2")

print(f"workflow exexuted in {run_time}\n{response}")


