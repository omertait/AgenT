import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from apiUtils import load_schema, save_schema, transform_schema_to_openai_format
from buildingBlocks.flowGraph import FlowGraph
from conversationManger import ConversationManager
from factories.agentsFactory import AgentsFactory
from factories.taskFunctionFactory import TaskFunctionFactory
from factories.tasksFactory import TaskFactory
from config.settings import import_client, interact_with_agent

# Initialize FastAPI app
app = FastAPI()

# Initialize global instances
llm_client = import_client()
agentsFactory = AgentsFactory(llm_client=llm_client)
taskFunctionFactory = TaskFunctionFactory()
taskFactory = TaskFactory()
flowGraph = FlowGraph()
conversation_manager = None


# Pydantic Models
class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool


class Tool(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    function: str


class Step(BaseModel):
    type: str
    promptTemplate: Optional[str] = None
    model: Optional[str] = None
    tool: Optional[str] = None
    input_data_func: Optional[str] = None
    memory_arg: Optional[str] = None


class NodeData(BaseModel):
    isStartNode: bool
    taskName: str
    agent: str
    steps: List[Step]


class Node(BaseModel):
    id: str
    type: str
    data: NodeData


class Edge(BaseModel):
    source: str
    target: str


class Agent(BaseModel):
    id: int
    name: str
    role: str
    tools: List[str]


class WorkflowSchema(BaseModel):
    agents: List[Agent]
    tools: List[Tool]
    nodes: List[Node]
    edges: List[Edge]


@app.post("/build")
def initialize_workflow(workflow: WorkflowSchema):
    global conversation_manager

    # Step 1: Add Tools
    for tool in workflow.tools:
        try:
            agentsFactory.toolsFactory.addTool(
                tool.name,
                tool.function,
                {"description": tool.description, **{param.name: param.type for param in tool.parameters}}
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Error adding tool {tool.name}: {str(e)}")

    # Step 2: Create Agents
    for agent in workflow.agents:
        agentsFactory.createAgent(
            name=agent.name,
            interact_func=interact_with_agent,  # Replace with actual interaction function
            role=agent.role,
            tools=agent.tools
        )

    # Step 3: Create Nodes and Tasks
    start_node_id = None
    for node in workflow.nodes:
        agent_instance = agentsFactory.getAgent(node.data.agent)
        steps = [step.model_dump() for step in node.data.steps]
        task_function = taskFunctionFactory.createTaskFunction(steps)
        task = taskFactory.createTask(agent_instance, task_function)
        flowGraph.add_task(node.id, task)
        if node.data.isStartNode:
            start_node_id = node.id

    # Step 4: Add Edges
    for edge in workflow.edges:
        flowGraph.add_edge(edge.source, edge.target)

    # Step 5: Set Start Node
    if start_node_id:
        flowGraph.set_start_node(start_node_id)
    else:
        raise HTTPException(status_code=400, detail="No start node specified in workflow.")

    # Step 6: Initialize Conversation Manager
    conversation_manager = ConversationManager(flowGraph, id="1")

    return {"status": "Workflow initialized successfully"}


class UserInput(BaseModel):
    user_input: str

@app.post("/run")
def run_workflow(user_input: UserInput):
    global conversation_manager

    if not conversation_manager:
        raise HTTPException(status_code=400, detail="Workflow not initialized.")

    try:
        response, run_time = conversation_manager.run(user_input.user_input)
        return {"response": response, "run_time": run_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# Load and transform the schema
original_schema = load_schema("schema.json")
openai_response_schema = transform_schema_to_openai_format(original_schema)
save_schema("transformed_schema.json", openai_response_schema)  # debug

class GenerateRequest(BaseModel):
    """Request model for the generate endpoint."""
    prompt: str


class GenerateResponse(BaseModel):
    """Response model for the generate endpoint."""
    workflow: Dict


@app.post("/generate", response_model=GenerateResponse)
def generate_workflow(request: GenerateRequest):
    """
    Generate a workflow JSON object based on the user's prompt.
    """
    try:
        # Prepare the prompt for the model
        llm_prompt = (
            f"Based on the following user prompt, generate a JSON object that adheres to the provided schema.\n\n"
            f"User Prompt: {request.prompt}\n\n"
            f"Ensure the output strictly complies with the schema."
        )

        # Call the OpenAI API with structured outputs
        response = llm_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant for creating structured JSON Agentic workflows."},
                {"role": "user", "content": llm_prompt}
            ],
            response_format=openai_response_schema
        )

        # Extract the structured JSON output
        generated_json = response.choices[0].message.content

        # Convert JSON string to a Python dictionary
        workflow = json.loads(generated_json)

        return {"workflow": workflow}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))