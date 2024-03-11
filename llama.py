from autogen import ConversableAgent

config_list = [{"model": "local-model",  "api_type": "openai", "api_key": "NULL", "base_url" :"http://localhost:1234/v1" }]

# Example one ====== BASIC local model
agent = ConversableAgent(
    "chatbot",
    llm_config={"config_list": config_list },
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)
reply = agent.generate_reply(messages=[{"content": "Tell me a joke.", "role": "user"}])
print(reply)
