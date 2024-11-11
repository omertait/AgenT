# AGenT Framework Documentation

## Overview
This framework is designed for building and executing intelligent, modular workflows that combine tasks, tools, and language model (LLM) interactions. It allows developers to create dynamic agents that handle complex tasks by chaining steps, interacting with tools, and making decisions based on conditions. The system is highly flexible and can support use cases ranging from conversational agents to workflow automation.

---

## Project Structure

### Main Components
1. **Agents**: Core entities executing workflows and managing tools.
2. **Tasks**: Defined units of work composed of steps.
3. **Steps**: Granular actions within tasks (e.g., LLM interaction, memory updates, tool usage).
4. **Flow Graph**: Represents workflows as a directed graph.
5. **Factories**: Responsible for creating agents, tasks, tools, and step handlers.

### Files
| File                    | Description                                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------------------------|
| `agentsFactory.py`      | Manages agent creation and assigns tools to agents.                                                           |
| `stepHandlers.py`       | Defines handlers for different step types (e.g., LLM interaction, tool usage).                                |
| `taskFunctionFactory.py`| Converts step specifications into executable task functions. Validates their structure.                       |
| `tasksFactory.py`       | Creates tasks by associating agents and task functions.                                                       |
| `toolsFactory.py`       | Manages tools, allowing dynamic addition of tools and their functions.                                        |
| `agent.py`              | Represents the agent entity that executes tasks and interacts with the LLM.                                   |
| `flowGraph.py`          | Implements a directed graph for workflow execution, supporting conditional branching and task chaining.        |
| `task.py`               | Defines the structure and execution logic for tasks.                                                          |
| `conversationManger.py` | Manages workflows in response to user input, maintains conversation history, and handles memory.               |
| `run.py`                | Example script demonstrating how to use the framework to create workflows, agents, and tasks.                 |

---

## Framework Details

### 1. Agents
Agents are the central entities responsible for executing workflows.

#### Constructor:
```python
Agent(name, llm_client, interact_func, role, step_handler)
```
- `name`: Agent's name (for reference).
- `llm_client`: LLM client instance.
- `interact_func`: Function to interact with the LLM.
- `role`: Role of the agent (system prompt).
- `step_handler`: StepHandler instance to handle steps.

#### Adding Tools:
```python
agent.add_tool(tool_name, tool_info)
```
- `tool_name`: Name of the tool.
- `tool_info`: A list containing the tool function and description.

---

### 2. Tools
Tools are functionalities that agents can use during workflows.

#### Adding Tools:
```python
toolsFactory.addTool(toolName, toolFunction, toolDescription)
```
- `toolName`: Unique name for the tool.
- `toolFunction`: String representation of the tool's Python function.
- `toolDescription`: Dictionary describing the tool's functionality and input parameters.

**Example Tool:**
```python
func = """def calculator_two_numbers(x, y, operation):
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
toolsFactory.addTool("calculator", func, {"description": "Performs basic arithmetic operations.", "x": "number", "y": "number", "operation": "string"})
```

---

### 3. Tasks
Tasks are modular units of work executed by agents. Each task consists of multiple **steps**.

#### Constructor:
```python
Task(agent, function)
```
- `agent`: The agent assigned to the task.
- `function`: A function defining the task's steps.

---

### 4. Steps
Steps are the individual actions within tasks. Each step defines a specific operation and its parameters.

#### General Step Structure
```python
step = {
    "type": "<step_type>",  # Required
    # Additional fields depending on the step type
}
```

#### Step Types
There are three main step types: 
1. **LLM Interaction (`llm_interact`)**
2. **Tool Interaction (`tool`)**
3. **Update Memory (`update_memory`)**

#### 1. **LLM Interaction (`llm_interact`)**
Allows the agent to query an LLM with a custom prompt. The prompt can reference:
- `{task_input}`: The input initially provided to the task.
- `{last_step_result}`: The result of the previous step.
- `{memory}`: The agent's memory.

**Fields:**
- `type`: `"llm_interact"`
- `promptTemplate`: A string template for the LLM prompt.
- `model` (optional): The LLM model to use. Default is `"gpt-4o-mini"`.

**Example:**
```python
step = {
    "type": "llm_interact",
    "promptTemplate": "Summarize the input: {task_input}. Use the previous result: {last_step_result}.",
    "model": "gpt-4o-mini"
}
```

---

#### 2. **Tool Interaction (`tool`)**
Executes a tool function with specified input data.

**Fields:**
- `type`: `"tool"`
- `tool`: The name of the tool to use.
- `input_data_func`: A string representation of a Python dictionary that defines the input arguments for the tool. This can reference:
  - `last_step_result`
  - `task_input`
  - `memory`

**Example:**
```python
step = {
    "type": "tool",
    "tool": "calculator",
    "input_data_func": '{"x": 2, "y": 3, "operation": "add"}'
}
```

---

#### 3. **Update Memory (`update_memory`)**
Updates the agent's memory with the result of the current step.

**Fields:**
- `type`: `"update_memory"`
- `update_memory_func` (optional): A function to handle the memory update.
- `memory_arg`: The key in the agent's memory to update.

**Example:**
```python
step = {
    "type": "update_memory",
    "memory_arg": "calculation_result"
}
```

---

### Full Example of Task Steps
A task with multiple steps:
1. Use the `calculator` tool to add two numbers.
2. Interact with the LLM to explain the result.
3. Store the result in memory.

```python
steps = [
    {
        "type": "tool",
        "tool": "calculator",
        "input_data_func": '{"x": 5, "y": 7, "operation": "add"}'
    },
    {
        "type": "llm_interact",
        "promptTemplate": "Explain the addition result: {last_step_result}.",
        "model": "gpt-4o-mini"
    },
    {
        "type": "update_memory",
        "memory_arg": "last_calculation"
    }
]
```

---

### 5. Flow Graph
The `FlowGraph` class represents workflows as directed graphs.

#### Constructor:
```python
FlowGraph()
```

#### Adding Nodes:
```python
flowGraph.add_task(node_id, task)
flowGraph.add_condition(node_id, condition_func)
```

- `node_id`: Identifier for the graph node.
- `task`: Task to execute.
- `condition_func`: Function to evaluate conditions.

#### Adding Edges:
```python
flowGraph.add_edge(from_node, to_node, condition=None)
```
- `from_node`: Starting node.
- `to_node`: Destination node.
- `condition`: Optional condition for the edge (used in conditional nodes).

#### Execution:
```python
result = flowGraph.run(input, memory)
```

#### Visualization:
```python
flowGraph.visualize(filename="flowgraph.png")
```

---

### 6. Conversation Manager
Handles workflows in response to user input.

#### Constructor:
```python
ConversationManager(flow_graph, id, memory=None)
```
- `flow_graph`: The workflow graph.
- `id`: Conversation ID.
- `memory`: Dictionary for storing conversation data.

#### Running a Workflow:
```python
response, run_time = conversationManager.run(user_input)
```

---

## Using the Framework

### Example: Create a Workflow
1. **Create Tools**:
```python
toolsFactory.addTool("calculator", func, {"description": "Performs arithmetic operations.", "x": "number", "y": "number", "operation": "string"})
```

2. **Create an Agent**:
```python
agent = agentsFactory.createAgent("John", interact_func, "friendly assistant", tools=["calculator"])
```

3. **Define Task Functions**:
```python
steps = [
    {"type": "tool", "tool": "calculator", "input_data_func": '{"x":5, "y":3, "operation":"multiply"}'},
    {"type": "llm_interact", "promptTemplate": "Provide a detailed explanation of the result: {last_step_result}", "model": "gpt-4o-mini"}
]
task_func = taskFunctionFactory.createTaskFunction(steps)
```

4. **Create Tasks**:
```python
task = taskFactory.createTask(agent, task_func)
```

5. **Build the Flow Graph**:
```python
flowGraph = FlowGraph()
flowGraph.add_task("start", task)
flowGraph.set_start_node("start")
```

6.

 **Run a Workflow**:
```python
conversationManager = ConversationManager(flowGraph, "conversation_1")
response, run_time = conversationManager.run("Calculate 5 * 3")
print(response)
```

---

## Features
- **Dynamic Tool Integration**: Add tools dynamically at runtime.
- **Customizable Workflows**: Create complex workflows using tasks and graphs.
- **Step References**:
  - `{task_input}`: Task's initial input.
  - `{last_step_result}`: Result of the previous step.
- **Visualization**: Generate visual representations of workflows.

This framework provides a flexible, modular way to build intelligent agents and workflows powered by tools and LLMs.