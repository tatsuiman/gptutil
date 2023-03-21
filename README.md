# GPT utility

English | [日本語](./README.ja-JP.md)

Command utility for creating your own AI assistant

## Installation
```
pip install gptutil
```

## Usage
* Ask ChatGPT questions in a pipeline:

```bash
export OPENAI_API_KEY="OpenAI API Key"

git clone git clone https://github.com/openai/evals/
cp evals/evals/registry/data/test_fuzzy_match/samples.jsonl .
cat samples.jsonl | gpt-ask 'Translate this.'
cat samples.jsonl | gpt-ask 'Translate this.' |jq |less
cat samples.jsonl | gpt-ask 'Translate this.' | gpt-ask 'Use jq to extract all "content" values with "role" equal to "user".'
```

* Debug commands interactively:
```bash
gpt-interact -n simple_chat
```
or
```bash
gpt-interact -n simple_chat -t gptutil/example/assistant.yaml
```

You can also customize your own assistant by modifying [this file](gptutil/example/assistant.yaml).

|Command|Description|
|---|---|
|@use AssistantName|Switches to a different assistant.|
|@history|Displays chat history.|
|@reset|Clears the input and chat history for the assistant.|
|@params| Show set assistant paramaters|
|! (e.g. !ls -l, !bash)|Executes a command in the middle of a question and displays the result.

|Assistant|Description|
|---|---|
|simple_chat|	Normal chat.|
|command_debug|	Displays solutions by executing commands and displaying error messages.|
|pentest|	Explains penetration testing tools and procedures step by step.|

## Demo
### Asking ChatGPT questions in a pipeline
![](./docs/img/gpt-tools.gif)
### Debugging commands interactively
![](./docs/img/ffmpeg-demo.gif)
