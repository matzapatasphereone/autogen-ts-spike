import os
from dotenv import load_dotenv
from typing_extensions import Annotated
import autogen
import subprocess

# =========== config =========== 
load_dotenv()

config_list = [{ 'model': 'gpt-3.5-turbo', 'api_key':  os.getenv('CHATGPT_API_KEY') }]
llm_config = { "config_list": config_list, "timeout": 240 }

current_dir = os.getcwd()
base_dir = os.path.join(current_dir, 'tmp')
os.makedirs(base_dir, exist_ok=True)


# =========== agents =========== 
# code_reviewer_agent will review the code provided and provide feedback
code_reviewer_agent = autogen.AssistantAgent(
    name="code_reviewer_agent",
    system_message="Execute code with the provided functions, check for errors and provide feedback. Use the provided functions to install dependencies and execute the code",
    llm_config=llm_config,
)
# software_engineer will write the code for the user
software_engineer_agent = autogen.AssistantAgent(
    name="software_engineer_agent",
    system_message="You're a senior software engineer specialized in typescript, write code to satisfy the user's request",
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
@code_reviewer_agent.register_for_llm(description="execute typescript code and return the result")
def execute_typescript_code(
    typescript_code: Annotated[str, ""],
) -> str:
    src_path = os.path.join(base_dir, 'temp.ts')
    out_path = os.path.join(base_dir, 'temp.js')
    
    # Write TypeScript code to a temporary file
    with open(src_path, "w") as file:
        file.write(typescript_code)

    # Compile TypeScript code to JavaScript
    subprocess.run(["tsc", src_path])

    # Execute generated JavaScript code
    result = subprocess.run(["node", out_path], capture_output=True, text=True)
    
    # Clean up temporary files
    # subprocess.run(["rm", src_path, out_path])

    succeeded = "Succeeded" if result.returncode == 0 else "Failed"
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return f"Program {succeeded}\nStdout:{stdout}\nStderr:{stderr}"

@user_proxy.register_for_execution()
@code_reviewer_agent.register_for_llm(description="execute bash scripts")
def execute_bash_scripts(
    bash_script: Annotated[str, ""],
) -> str:

    # Execute bash script
    result = subprocess.run(["bash", "-c", bash_script], capture_output=True, text=True, cwd=base_dir)
    
    succeeded = "Succeeded" if result.returncode == 0 else "Failed"
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return f"Bash script {succeeded}\nStdout:{stdout}\nStderr:{stderr}"


#  =========== main =========== 
res = user_proxy.initiate_chat(
    manager, 
    message="Use randomstring library to create random strings in typescript"
            " software_engineer_agent will generate the code to solve the user's request," 
            " code_reviewer_agent will execute the code generated and check it works as expected",
)