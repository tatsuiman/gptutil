# GPT Tools

## インストール
```
pip install gpt-tools
```

## 使い方
```bash
git clone git clone https://github.com/openai/evals/
cp evals/evals/registry/data/test_fuzzy_match/samples.jsonl .
cat samples.jsonl | gpt-ask '翻訳して'
cat samples.jsonl | gpt-ask '翻訳して' |jq |less
cat samples.jsonl | gpt-ask '翻訳して' | gpt-ask 'jq を使ってrole = "user"の "content"をすべて取り出して下さい。'
```

## Demo
![](./docs/img/gpt-tools.gif)