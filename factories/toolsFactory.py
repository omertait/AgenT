
class ToolsFactory:
    def __init__(self):
        self.tools = {}

    
    def addTool(self, toolName, toolFunction):
        if toolName in self.tools:
            raise ValueError(f'Tool with name {toolName} already exists')
        
        self.tools[toolName] = toolFunction

    def getTool(self, toolName):
        return self.tools[toolName]
    

    


