import sys
import openai
import tiktoken
from retry import retry

class Tokenizer:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)

    def split_token(self, text, chunk_size=4096):
        tokens = self.encoding.encode(text, allowed_special="all")
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk = self.encoding.decode(tokens[start:end])
            chunks.append(chunk)
            start = end
        return chunks

    def calc_token(self, text):
        return len(self.encoding.encode(text, allowed_special="all"))

    def calc_price(self, text):
        # https://openai.com/pricing
        model_price = {
            "ada": 0.0000004,
            "text-ada-001": 0.0000004,
            "babbage": 0.0000005,
            "text-babbage-001": 0.0000005,
            "curie": 0.000002,
            "text-curie-001": 0.000002,
            "davinci": 0.00002,
            "text-davinci-001": 0.00002,
            "code-davinci-002": 0.00002,
            "text-davinci-002": 0.00002,
            "text-davinci-003": 0.00002,
            "gpt-3.5-turbo": 0.000002,
            "gpt-3.5-turbo-0301": 0.000002,
            "gpt-4": 0.00003,
            "gpt-4-0314": 0.00003,
            "gpt-4-32K": 0.00006,
            "gpt-4-32K-0314": 0.00006,
        }
        token_count = self.calc_token(text)
        return token_count * model_price[model]

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
