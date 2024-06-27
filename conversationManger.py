
class ConversationManager:
    def __init__(self, flow_graph, id, memory=None):
        self.flow_graph = flow_graph
        self.memory = memory if memory is not None else {
            'user_input': None,
            'conversation_history': [],
        }
       

    def set_id(self, conversation_id):
        self.memory['conversation id'] = conversation_id


    def run(self, user_input):
        self.memory['user_input'] = user_input
        self.memory['conversation_history'].append({"role": "user", "content": user_input})
        response = self.flow_graph.run(user_input, self.memory)
        if response is not None or response != "":
            self.memory['conversation_history'].append({"role": "assistant", "content": response})
        return response
    
    def run_out_of_conversation(self, user_input):
        response = self.flow_graph.run(user_input, self.memory)
        return response

