import os
import re
import sys
import time
import yaml
import click
import gptutil
import subprocess
import pkg_resources
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from .chat import Chat
from .agent import BashAgent

EXAMPLE_TEMPLATE = example_path = os.path.join(gptutil.__path__[0], "example", "assistant.yaml")

def replace_commands(input_str):
    def replace_env_var(match):
        return os.environ.get(match.group(1), '')

    def replace_command(match):
        try:
            result = subprocess.check_output(match.group(1), shell=True, text=True)
            return result.strip()
        except subprocess.CalledProcessError:
            return ''

    # 環境変数を置き換える
    replaced_str = re.sub(r'\${(\w+)}', replace_env_var, input_str)
    # コマンドを置き換える
    replaced_str = re.sub(r'`(\w+)`', replace_command, replaced_str)
    return replaced_str

class CLIHandler:
    def __init__(self, template):
        self.template = template
        self.assistant_name = None
        self.chat = Chat()
        self.bash_agent = BashAgent()
        self.data = {}

    def handle_command(self, assistant_name):
        self.assistant_name = assistant_name
        assistant = self.template[self.assistant_name]

        history_config = assistant.get("history", {})
        if history_config.get("type") == "file":
            history_file = os.path.expanduser(history_config.get("path", "~/.gpt_interact_history"))
            history = FileHistory(history_file)
            chat_log_dir = os.path.expanduser("~/.gpt_history")
            os.makedirs(chat_log_dir, exist_ok=True)
            self.chat.set_log_file(os.path.join(chat_log_dir, f"{assistant_name}.log"))
        else:
            history = InMemoryHistory()

        commands_completer = WordCompleter(
            ["@use", "@history", "@reset", "@params"] + list(self.template.keys()),
            meta_dict={
                "@use": "Switch assistant",
                "@reset": "Reset chat",
                "@history": "Show chat history",
                "@params": "Show params",
            },
        )

        session = PromptSession(history=history, completer=commands_completer, complete_while_typing=True)

        system_prompt = None
        self.data = {}
        for item in assistant["params"]:
            if item["type"] == "once":
                command, new_assistant = self.handle_params(session, self.assistant_name, item)
                if new_assistant:
                    return new_assistant
                self.data[item["name"]] = command
            if item["type"] == "static":
                static_value = replace_commands(item["value"])
                self.data[item["name"]] = static_value
                print(f"[{assistant_name}] {item['name']}: {static_value}")
            system_prompt = assistant.get("system_prompt", "").format(**self.data)

        self.chat.reset(system_prompt)

        while True:
            for item in assistant["params"]:
                if item["type"] == "each":
                    command, new_assistant = self.handle_params(session, self.assistant_name, item)
                    if new_assistant:
                        return new_assistant
                    self.data[item["name"]] = command
            answer = self.chat.ask(assistant["user_prompt"].format(**self.data))
            agent = assistant.get("agent", {})
            if agent.get("name") == "bash":
                while True:
                    cmd_result = self.bash_agent.run(answer)
                    print("\033[32m" + cmd_result + "\033[0m")
                    if cmd_result == "":
                        cmd_result = replace_commands(agent.get("args", ""))
                    time.sleep(5)
                    answer = self.chat.ask(cmd_result)

    def handle_at_command(self, command):
        if command.startswith("@use "):
            new_assistant = command[5:].strip()
            if new_assistant in self.template:
                return command, new_assistant
        elif command.startswith("@reset"):
            self.chat.reset()
            return command, self.assistant_name
        elif command.startswith("@history"):
            self.chat.show_history()
            return None, None
        elif command.startswith("@params"):
            for key in self.data.keys():
                value = self.data[key]
                print(f"{key}: {value}")
            return None, None
        else:
            print(f"{command} not found")
            return None, None
        return command, None

    def handle_params(self, session, assistant_name, item):
        while True:
            command = session.prompt(f"[{assistant_name}] {item['value']}: ")
            command = item.get("default") if command is None else command
            if command.startswith("@"):
                command, new_assistant = self.handle_at_command(command)
                if new_assistant:
                    return None, new_assistant
            if command is None:
                continue
            if command.lower() == "exit":
                sys.exit()
            if command.startswith("!"):
                command = command[1:].strip()
                if command == "":
                    command = os.environ.get("SHELL", "bash")
                os.system(command)
            else:
                return command, None


@click.command()
@click.option(
    "-t",
    "--template",
    "template_file",
    type=click.File("r"),
    default=EXAMPLE_TEMPLATE,
    help="Template file in yaml format",
)
@click.option("-n", "--name", "assistant_name", type=str, help="Name of assistant")
def main(template_file, assistant_name):
    template = yaml.safe_load(template_file)
    handler = CLIHandler(template)
    while True:
        assistant_name = handler.handle_command(assistant_name)


if __name__ == "__main__":
    main()
