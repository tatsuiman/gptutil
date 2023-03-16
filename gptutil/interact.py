import os
import sys
import yaml
import click
import gptutil
import pkg_resources
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from .chat import Chat

EXAMPLE_TEMPLATE = example_path = os.path.join(gptutil.__path__[0], 'example', 'assistant.yaml')

class CLIHandler:
    def __init__(self, template):
        self.template = template
        self.assistant_name = None

    def handle_command(self, assistant_name):
        self.assistant_name = assistant_name
        assistant = self.template[self.assistant_name]

        history_config = assistant.get("history", {})
        if history_config.get("type") == "file":
            history_file = history_config.get("path", "~/.gpt_interact_history")
            history = FileHistory(os.path.expanduser(history_file))
        else:
            history = InMemoryHistory()

        commands_completer = WordCompleter(['@use', '@reset'] + list(self.template.keys()), meta_dict={'@use': 'Switch assistant', '@who': 'Reset chat'})

        session = PromptSession(history=history, completer=commands_completer, complete_while_typing=True)

        system_prompt = None
        data = {}
        for item in assistant["params"]:
            if item["type"] == "once":
                command = session.prompt(f"[{self.assistant_name}] {item['name']}: ")
                command = item.get("default") if command is None else command  
                new_assistant = self.handle_at_command(command)
                if new_assistant:
                    return new_assistant
                data[item["value"]] = command
            system_prompt = assistant.get("system_prompt", "").format(**data)

        chat = Chat(system_prompt)

        while True:
            for item in assistant["params"]:
                if item["type"] == "each":
                    command, new_assistant = self.handle_each(session, self.assistant_name, item)
                    if new_assistant:
                        return new_assistant
                    data[item["value"]] = command
            chat.ask(assistant["user_prompt"].format(**data))
            print("")

    def handle_at_command(self, command):
        if command.startswith("@use "):
            new_assistant = command[5:].strip()
            if new_assistant in self.template:
                return new_assistant
        if command.startswith("@reset"):
            return self.assistant_name
        return None

    def handle_each(self, session, assistant_name, item):
        while True:
            command = session.prompt(f"[{assistant_name}] {item['name']}: ")
            command = item.get("default") if command is None else command  
            if command.lower() == "exit":
                sys.exit()
            new_assistant = self.handle_at_command(command)
            if new_assistant:
                return None, new_assistant
            if command.startswith("!"):
                command = command[1:].strip()
                if command == "":
                    command = os.environ.get("SHELL", "bash")
                os.system(command)
            else:
                return command, None


@click.command()
@click.option("-t", "--template", "template_file", type=click.File("r"), default=EXAMPLE_TEMPLATE, help="Template file in yaml format")
@click.option("-n", "--name", "assistant_name", type=str, help="Name of assistant")
def main(template_file, assistant_name):
    template = yaml.safe_load(template_file)
    handler = CLIHandler(template)
    while True:
        assistant_name = handler.handle_command(assistant_name)


if __name__ == "__main__":
    main()

