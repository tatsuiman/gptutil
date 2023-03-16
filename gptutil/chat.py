import sys
import openai

class Chat:
    def __init__(self, system_prompt=None):
        self.messages = []
        self.max_token = False
        if system_prompt is not None:
            self.messages.append({"role": "system", "content": system_prompt})

    def ask(self, prompt, model="gpt-3.5-turbo", temperature=0.5, max_tokens=1024):
        report = []
        self.messages.append({"role": "user", "content": prompt})

        def _ask():
            if self.max_token:
                self.messages.pop(1)
                print("トークン数が足りません。過去の会話履歴を削除しました")
            for resp in openai.ChatCompletion.create(
                model=model,
                messages=self.messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            ):
                token = resp["choices"][0]["delta"].get("content", "")
                report.append(token)
                sys.stdout.write(token)
                sys.stdout.flush()
            answer = "".join(report).strip().replace("\n", "")
            self.messages.append({"role": "assistant", "content": answer})
        try:
            _ask()
        except:
            self.max_token = True
            _ask()
