import os
import sys
import hashlib
import click
import openai
from .chat import Tokenizer


@click.command()
@click.option("--model", "-m", default="gpt-3.5-turbo", help="Model to use for translation.")
@click.option("--temperature", "-t", default=0.7, type=float, help="Temperature for sampling.")
@click.option("--max_tokens", "-M", default=1024, type=int, help="Maximum number of tokens in the output.")
@click.option("--chunk_size", "-C", default=2048, type=int, help="Standerd input split token size")
@click.option("--overwrite", "-w", is_flag=True, help="Overwrite cached result.")
@click.option("--verbose", "-v", is_flag=True, help="Display cost information.")
@click.argument("prompt", type=click.STRING, default="", required=False)
def main(model, temperature, max_tokens, chunk_size, overwrite, verbose, prompt):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    tokenizer = Tokenizer(model)
    if not openai.api_key:
        print("環境変数にOpenAI API キーが設定されていません。")
        return

    contents = []
    std_in = ""
    if not sys.stdin.isatty():
        std_in = sys.stdin.read()
        prompt_token_size = tokenizer.calc_token(prompt + "\n")
        chunk_size = chunk_size - prompt_token_size
        contents = [f"{prompt}\n{content}" for content in tokenizer.split_token(std_in, chunk_size)]
    else:
        contents.append(prompt)

    if prompt == "" and std_in == "":
        print("プロンプトが空です")
        return

    price = 0
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "gptutil")
    os.makedirs(cache_dir, exist_ok=True)

    for content in contents:
        prompt_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        cache_file_path = os.path.join(cache_dir, f"{prompt_hash}.txt")
        if not overwrite and os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as cache_file:
                cache = cache_file.read()
                print(cache)
                continue
        else:
            if verbose:
                price += tokenizer.calc_price(content)
                print(f"token: {tokenizer.calc_token(content)} price: {price} USD")

        with open(cache_file_path, "w") as cache_file:
            for resp in openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            ):
                token = resp["choices"][0]["delta"].get("content", "")
                cache_file.write(token)
                sys.stdout.write(token)
                sys.stdout.flush()


if __name__ == "__main__":
    main()
