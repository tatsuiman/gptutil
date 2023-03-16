# GPT utility

## インストール
```
pip install gptutil
```

## 使い方
* パイプラインでChatGPTに質問する
```bash
export OPENAI_API_KEY="OpenAI API Key"

git clone git clone https://github.com/openai/evals/
cp evals/evals/registry/data/test_fuzzy_match/samples.jsonl .
cat samples.jsonl | gpt-ask '翻訳して'
cat samples.jsonl | gpt-ask '翻訳して' |jq |less
cat samples.jsonl | gpt-ask '翻訳して' | gpt-ask 'jq を使ってrole = "user"の "content"をすべて取り出して下さい。'
```
* インタラクティブにコマンドのデバッグを行う
```bash
gpt-interact -n simple_chat
```
|コマンド|説明|
|---|---|
|@use アシスタント名|アシスタントを切り替えてチャット履歴を削除します|
|@reset|アシスタントの入力値とチャット履歴を削除します|
|! (例：!ls -l, !bash)|質問の途中でコマンドを実行し結果を表示します。|

|アシスタント|説明|
|---|---|
|simple_chat|通常のチャットです|
|command_debug|コマンドの実行とエラー内容を入力することで解決策を表示し続けます|
|pentest|ペネトレーションの手順やツールの解説をステップバイステップで説明します|

## Demo
* パイプラインでChatGPTに質問する
![](./docs/img/gpt-tools.gif)
* インタラクティブにコマンドのデバッグを行う
![](./docs/img/ffmpeg-demo.gif)
