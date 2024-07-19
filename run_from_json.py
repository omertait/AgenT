import json
from buildingBlocks.flowGraph import FlowGraph
from conversationManger import ConversationManager
from factories.agentsFactory import AgentsFactory
from factories.taskFunctionFactory import TaskFunctionFactory
from factories.tasksFactory import TaskFactory
from config.settings import import_client, interact_with_agent

# Load the JSON data
with open('config.json') as f:
    config = json.load(f)

llm_client = import_client()

# Setup AgentsFactory and add tools
agentsFactory = AgentsFactory(llm_client=llm_client)
for tool in config['tools']:
    agentsFactory.toolsFactory.addTool(
        tool['name'],
        tool['function'],
        {
            "description": tool['description'],
            **tool['parameters']
        }
    )

# Create agent
agent_config = config['agent']
agent = agentsFactory.createAgent(agent_config['name'], interact_with_agent, agent_config['role'], tools=agent_config['tools'])

# Setup TaskFunctionFactory and create task functions
taskFunctionFactory = TaskFunctionFactory()
task_functions = {}
for task_function in config['task_functions']:
    steps = task_function['steps']
    task_functions[task_function['name']] = taskFunctionFactory.createTaskFunction(steps)

# Setup TaskFactory and create tasks
taskFactory = TaskFactory()
tasks = {}
for task in config['tasks']:
    tasks[task['name']] = taskFactory.createTask(agent, task_functions[task['function']])

# Setup FlowGraph
flow_graph = FlowGraph()
for task in config['flow_graph']['tasks']:
    flow_graph.add_task(task['name'], tasks[task['task']])

flow_graph.set_start_node(config['flow_graph']['start_node'])

for edge in config['flow_graph']['edges']:
    flow_graph.add_edge(edge['from'], edge['to'])

# Setup ConversationManager and run
conversation_config = config['conversation_manager']
conversationManager = ConversationManager(flow_graph, conversation_config['conversation_id'])
response, run_time = conversationManager.run(conversation_config['input'])

print(f"workflow executed in {run_time}\n{response}")
