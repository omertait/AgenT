
import ast


class ToolsFactory:
    def __init__(self):
        self.tools = {}

    
    def addTool(self, toolName, toolFunction, toolDescription):
        if toolName in self.tools:
            raise ValueError(f'Tool with name {toolName} already exists')
        
        tool_function_code = self.parse(toolFunction)
        
        self.tools[toolName] = [tool_function_code, toolDescription]

    def getTool(self, toolName):
        return self.tools[toolName]
    
    def parse(self, tool_function_str):
        # Parse and compile the function string
        tree = ast.parse(tool_function_str, mode='exec')
        code = compile(tree, '<string>', 'exec')
        
        # Create a namespace dictionary to execute the code in
        namespace = {}
        
        # Execute the compiled code to define the function in the namespace
        exec(code, namespace)
        
        # Get the function reference from the namespace
        function_name = list(namespace.keys())[1]  # The first key is '__builtins__'

        function_ref = namespace[function_name]
        return function_ref
    
    

    


