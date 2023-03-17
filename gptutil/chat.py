import sys
import openai
from retry import retry


class Chat:
    def __init__(self):
        self.messages = [{"role": "system", "content": ""}]
        self.max_token_used = False

    def reset(self):
        self.messages = [{"role": "system", "content": ""}]

    def set_system(self, prompt):
        self.messages[0].update({"content": prompt})

    def show_history(self):
        for message in self.messages:
            if message["role"] == "user":
                print("\033[32m" + f"[{message['role']}] {message['content']}" + "\033[0m")
            elif message["role"] == "assistant":
                print("\033[33m" + f"[{message['role']}] {message['content']}" + "\033[0m")
            elif message["role"] == "system":
                print("\033[31m" + f"[{message['role']}] {message['content']}" + "\033[0m")

    @retry(tries=3, exceptions=(Exception,), delay=1, backoff=1)
    def _ask(self, prompt, model, temperature, max_tokens, max_token_used=False):
        if max_token_used:
            self.messages.pop(1)
            print("トークン数が足りません。過去の会話履歴を削除しました")

        report = []
        self.messages.append({"role": "user", "content": prompt})

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
        print("")

        answer = "".join(report)
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    def ask(self, prompt, model="gpt-3.5-turbo", temperature=0.5, max_tokens=1024):
        try:
            return self._ask(prompt, model, temperature, max_tokens)
        except Exception as e:
            try:
                return self._ask(prompt, model, temperature, max_tokens, max_token_used=True)
            except Exception as e:
                print(f"リトライが上限に達したため、処理を停止します。エラー内容: {str(e)}")
        return ""
