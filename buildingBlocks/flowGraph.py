import networkx as nx
import matplotlib.pyplot as plt

from buildingBlocks.task import Task


class ConditionNode:
    def __init__(self, condition_function):
        self.condition_function = condition_function
        self.edges = {}


    def add_edge(self, condition, next_node):
        self.edges[condition] = next_node

    def get_next_node(self, result, memory):
        condition_result = self.condition_function(result, memory)
        return self.edges.get(condition_result, None)


class FlowGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.start_node = None

    def add_task(self, node_id, task):
        self.nodes[node_id] = task

    def add_condition(self, node_id, condition_func):
        condition_node = ConditionNode(condition_func)
        self.nodes[node_id] = condition_node

    def add_edge(self, from_node, to_node, condition=None):
        '''
        from_node: str
        to_node: str
        condition: any, depends on the condition function
        ** note that the condition is relevant only to ConditionNode **
        regular nodes can have multiple outgoing edges,
        ConditionNode can have as many as the possible values of the condition
        '''
        if from_node in self.nodes:
            if isinstance(self.nodes[from_node], ConditionNode):
                self.nodes[from_node].add_edge(condition, to_node)
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append((to_node, None)) 

    def set_start_node(self, node_id):
        self.start_node = node_id

    def run(self, input, memory):
        '''
        input: str
        memory: dict
        iterate over the nodes and execute the tasks
        end the iteration when reach a node that doesn't have an outgoing edge
        '''
        current_node = self.start_node
        result = input
        while current_node is not None:
            node = self.nodes[current_node]
            if isinstance(node, Task):
                result = node.execute(result=result, memory=memory)
                print(f"Task {current_node} executed successfully.\nResult:\n{result}\n\n")
                next_node = None
                if current_node in self.edges:
                    next_node = self.edges[current_node][0][0]
                current_node = next_node
            elif isinstance(node, ConditionNode):
                next_node = node.get_next_node(result, memory)
                current_node = next_node
            else:
                break
        return result

    def visualize(self, filename="flowgraph.png"):
        '''
        visualize the flow graph using networkx and matplotlib
        '''
        G = nx.DiGraph()

        for node_id, node in self.nodes.items():
            label = f"{node_id}\n({node.agent.name})" if isinstance(node, Task) else node_id
            shape = "ellipse" if isinstance(node, Task) else "diamond"
            G.add_node(node_id, label=label, shape=shape)
        
        for from_node, edges in self.edges.items():
            for to_node, condition in edges:
                label = str(condition) if condition is not None else ""
                G.add_edge(from_node, to_node, label=label)
        
        for node_id, node in self.nodes.items():
            if isinstance(node, ConditionNode):
                for condition, next_node in node.edges.items():
                    label = str(condition)
                    G.add_edge(node_id, next_node, label=label)

        pos = nx.spring_layout(G)
        labels = nx.get_node_attributes(G, 'label')
        edge_labels = nx.get_edge_attributes(G, 'label')

        nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

        plt.savefig(filename)
        plt.show()
        print(f"Graph visualization saved as {filename}")



