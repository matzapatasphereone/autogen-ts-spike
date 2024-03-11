import os
from dotenv import load_dotenv
from typing_extensions import Annotated
import autogen
import subprocess

# =========== config =========== 
load_dotenv()

config_list = [{ 'model': 'gpt-3.5-turbo', 'api_key':  os.getenv('CHATGPT_API_KEY') }]
llm_config = { "config_list": config_list, "timeout": 240 }

# =========== agents =========== 
# code_reviewer_agent will review the code provided and provide feedback
code_reviewer_agent = autogen.AssistantAgent(
    name="code_reviewer_agent",
    system_message="Execute code with the provided functions, check for errors and provide feedback",
    llm_config=llm_config,
)
# software_engineer will write the code for the user
software_engineer_agent = autogen.AssistantAgent(
    name="software_engineer_agent",
    system_message="You're a senior software engineer specialized in nodejs, write code to satisfy the user's request",
    llm_config=llm_config,
)
# User proxy agent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().upper().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=4, 
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    },    
)

# =========== group chat and manager definitions ===========
group_chat = autogen.GroupChat(agents=[user_proxy, code_reviewer_agent, software_engineer_agent], messages=[], max_round=5)
manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

# =========== function definitions =========== 
@user_proxy.register_for_execution()
@code_reviewer_agent.register_for_llm(description="execute nodejs code and return the result")
def execute_nodejs_code(
    code: Annotated[str, ""],
) -> str:
    result = subprocess.run(["node", "-e", code], capture_output=True, text=True)

    succeeded = "Succeeded" if result.returncode == 0 else "Failed"
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return f"Program {succeeded}\nStdout:{stdout}\nStderr:{stderr}"


#  =========== main =========== 
res = user_proxy.initiate_chat(
    manager, 
    message="Build a json string parser in nodejs"
            " software_engineer_agent will generate the code to solve the user's request," 
            " code_reviewer_agent will execute the code generated and check it works as expected",
)