import re
import os
import tempfile
import subprocess

class PythonAgent:
    def extract_code_block(self, text):
        return re.findall(r"```python\n(.*?)\n```", text, re.DOTALL)

    def execute_code_block(self, code_block):
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
        return f"# 実行結果\n```\n{result}\n```"

    def run(self, instructions):
        result = ""
        # markdownのコードブロックを抽出し、それぞれを実行する
        for code_block in self.extract_code_block(instructions):
            # 実行結果を取得してresultに追加する
            result += self.execute_code_block(code_block) + "\n"
        return result.strip()
