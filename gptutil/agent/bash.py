import re
import os
import subprocess


class BashAgent:
    def __init__(self):
        self.environment = os.environ.copy()
        self.current_directory = os.getcwd()
        self.command_history = []

    def extract_commands(self, text):
        return re.findall(r'```\n(.*?)\n```', text, re.DOTALL)

    def execute_single_command(self, command, shell):
        command_parts = command.split(" ")
        if command_parts[0] == "cd":
            target_directory = command_parts[1]
            if not os.path.isabs(target_directory):
                target_directory = os.path.join(self.current_directory, target_directory)
            target_directory = os.path.abspath(target_directory)

            if os.path.isdir(target_directory):
                self.current_directory = target_directory
        if command_parts[0] == "export":
            key, value = command_parts[1].split("=")
            self.environment[key] = value

        shell.stdin.write(command + "\n")
        shell.stdin.flush()

        self.command_history.append(command)

    def execute_command_block(self, command_block):
        with subprocess.Popen(["bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.environment, cwd=self.current_directory) as shell:
            command_lines = command_block.split("\n")
            formatted_commands = "\n".join([f"$ {cmd}" for cmd in command_lines])

            for command in command_lines:
                self.execute_single_command(command, shell)

            stdout, stderr = shell.communicate()
            output = stdout if stdout else stderr

            return f"```\n{formatted_commands}\n```\n実行結果\n```\n{output}```\n"

    def run(self, instructions):
        commands = self.extract_commands(instructions)
        result = ""

        for command_block in commands:
            output = self.execute_command_block(command_block)
            result += output

        return result
