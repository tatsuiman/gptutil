import sys
import tiktoken
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationSummaryBufferMemory,
    ConversationBufferWindowMemory,
    ConversationEntityMemory,
    ConversationKGMemory,
)

# ConversationBufferMemory: 単純に会話記録を保持し、プロンプトに過去会話として入れ込むメモリです
# ConversationSummaryMemory: 会話の要約を保存するメモリです
# ConversationEntityMemory: 会話中の特定の事物にかんして保持するためのメモリです
#                           欠点としては、固有名詞抽出を行っているので表記ゆれに弱いことです
BASE_PROMPT = """
Context:
{entities}
Last line:
{input}
"""


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
    def __init__(self, model="gpt-3.5-turbo", temperature=0, max_tokens=2048):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.log_file = None
        self.memory = None
        self.reset()

    def reset(self, prompt=None):
        # chatプロンプトテンプレートの準備
        messages = []
        if prompt is not None:
            messages.append(SystemMessagePromptTemplate.from_template(prompt))
        messages.append(MessagesPlaceholder(variable_name="history"))
        messages.append(HumanMessagePromptTemplate.from_template("{input}"))
        #messages.append(HumanMessagePromptTemplate.from_template(BASE_PROMPT))
        prompt_template = ChatPromptTemplate.from_messages(messages)

        # チャットモデルの準備
        llm = ChatOpenAI(
            streaming=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=True,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        # メモリの準備
        # self.memory = ConversationBufferMemory(return_messages=True)
        self.memory = ConversationBufferWindowMemory(return_messages=True)
        # self.memory = ConversationSummaryMemory(llm=llm, return_messages=True)
        # self.memory = ConversationSummaryBufferMemory(llm=llm, return_messages=True)
        # self.memory = ConversationEntityMemory(llm=llm, return_messages=True)
        # self.memory = ConversationKGMemory(llm=llm, return_messages=True)
        # 会話チェーンの準備
        self.conversation = ConversationChain(memory=self.memory, prompt=prompt_template, llm=llm)
        self.messages = []

    def set_log_file(self, log_file):
        self.log_file = log_file

    def show_history(self):
        for message in self.messages:
            if message["role"] == "user":
                print("\033[32m" + f"[{message['role']}] {message['content']}" + "\033[0m")
            elif message["role"] == "assistant":
                print("\033[33m" + f"[{message['role']}] {message['content']}" + "\033[0m")
            elif message["role"] == "system":
                print("\033[31m" + f"[{message['role']}] {message['content']}" + "\033[0m")

    def write_log(self):
        if self.log_file is None:
            return
        with open(self.log_file, "a") as f:
            f.write(f"[{self.messages[-2]['role']}] {self.messages[-2]['content']}\n")
            f.write(f"[{self.messages[-1]['role']}] {self.messages[-1]['content']}\n")

    def ask(self, prompt):
        answer = ""
        try:
            answer = self.conversation.predict(input=prompt)
            print("")
            for message in self.memory.chat_memory.messages:
                if isinstance(message, ChatMessage):
                    self.messages.append({"role": message.role, "content": message.content})
                elif isinstance(message, HumanMessage):
                    self.messages.append({"role": "user", "content": message.content})
                elif isinstance(message, AIMessage):
                    self.messages.append({"role": "assistant", "content": message.content})
                elif isinstance(message, SystemMessage):
                    self.messages.append({"role": "system", "content": message.content})
            self.write_log()
        except Exception as e:
            print(e)

        return answer
