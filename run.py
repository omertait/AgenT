from buildingBlocks.flowGraph import FlowGraph
from conversationManger import ConversationManager
from factories.agentsFactory import AgentsFactory
from factories.taskFunctionFactory import TaskFunctionFactory
from factories.tasksFactory import TaskFactory
from config.settings import import_client, interact_with_agent

llm_client = import_client()


# Usage
agentsFactory = AgentsFactory(llm_client=llm_client)
agent = agentsFactory.createAgent("John", interact_with_agent, "friend", tools=[])

taskFunctionFactory = TaskFunctionFactory()
task_hello_func = taskFunctionFactory.createTaskFunction([{"type" : "llm_interact", "promptTemplate" : "responed to the following: {task_input}\n\nact as a friend.", "model": "gpt-3.5-turbo"}])
task_summ_func = taskFunctionFactory.createTaskFunction([{"type" : "llm_interact", "promptTemplate" : "summarize to one sentence: {task_input}", "model": "gpt-3.5-turbo"}])

taskFactory= TaskFactory()
task = taskFactory.createTask(agent, task_hello_func)
task_summ = taskFactory.createTask(agent, task_summ_func)

flow_graph = FlowGraph()
flow_graph.add_task("start" , task)
flow_graph.add_task("summary" , task_summ)
flow_graph.set_start_node("start")
flow_graph.add_edge("start", "summary")

conversationManager = ConversationManager(flow_graph, "1")
response = conversationManager.run("im am afraid that i will fail")

print(response)


