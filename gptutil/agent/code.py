import re
import os
import tempfile
import subprocess

class CodeAgent:
    def __init__(self):
        self.environment = os.environ.copy()
        self.current_directory = os.getcwd()
        self.command_history = []

    def extract_code_block(self, text):
        return re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)

    def extract_commands(self, text):
        return re.findall(r"```bash\n(.*?)\n```", text, re.DOTALL)

    def execute_code_block(self, code_block):
        os.chdir(self.current_directory)
        result = ""
        # ランダムなファイル名で一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            filename = f.name
            # 一時ファイルにコードブロックを書き込む
            f.write(code_block)
        # pythonコマンドから一時ファイルを実行し、標準出力を受け取る
        result = subprocess.check_output(["python", filename]).decode().strip()
        # 一時ファイルを削除する
        os.remove(filename)
        return f"\n#current directory: {self.current_directory}\n# python 実行結果\n```\n{result}\n```"

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
        with subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment,
            cwd=self.current_directory,
        ) as shell:
            command_lines = command_block.split("\n")
            formatted_commands = "\n".join(command_lines)

            for command in command_lines:
                self.execute_single_command(command, shell)

            stdout, stderr = shell.communicate()
            output = stdout if stdout else stderr

            return f"```\n{formatted_commands}\n```\n#current directory: {self.current_directory}\n#実行結果\n```\n{output}```\n"

    def run(self, instructions):
        result = ""
        try:
            commands = self.extract_commands(instructions)

            # bashのコマンドブロックを抽出し、それぞれを実行する
            for command_block in commands:
                output = self.execute_command_block(command_block)
                result += output

            # pythonのコードブロックを抽出し、それぞれを実行する
            for code_block in self.extract_code_block(instructions):
                result += self.execute_code_block(code_block) + "\n"

        except Exception as e:
            return str(e)

        return result
