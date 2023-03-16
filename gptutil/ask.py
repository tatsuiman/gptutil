import os
import sys
import hashlib
import click
import openai
import tiktoken

@click.command()
@click.option("--model", "-m", default="gpt-3.5-turbo", help="Model to use for translation.")
@click.option("--temperature", "-t", default=0.7, type=float, help="Temperature for sampling.")
@click.option("--max_tokens", "-M", default=1024, type=int, help="Maximum number of tokens in the output.")
@click.option("--overwrite", "-w", is_flag=True, help="Overwrite cached result.")
@click.option("--verbose", "-v", is_flag=True, help="Display cost information.")
@click.argument("prompt", type=click.STRING, default="", required=False)
def main(model, temperature, max_tokens, overwrite, verbose, prompt):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    if not openai.api_key:
        print("環境変数にOpenAI API キーが設定されていません。")
        return

    if not sys.stdin.isatty():
        content = sys.stdin.read()
        prompt = f"{prompt}\n{content}"

    if prompt == "":
        print("プロンプトが空です")
        return

    price = 0
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "gpt-tools")
    os.makedirs(cache_dir, exist_ok=True)

    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    cache_file_path = os.path.join(cache_dir, f"{prompt_hash}.txt")

    if not overwrite and os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as cache_file:
            text = cache_file.read()
        print(text)
    else:
        with open(cache_file_path, "w") as cache_file:
            for resp in openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            ):
                token = resp["choices"][0]["delta"].get("content", "")
                cache_file.write(token)
                sys.stdout.write(token)
                sys.stdout.flush()

        if verbose:
            with open(cache_file_path, "r") as cache_file:
                text = cache_file.read()
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
            encoding = tiktoken.encoding_for_model(model)
            token_count = len(encoding.encode(text, allowed_special="all"))
            price = token_count * model_price[model]
    if verbose:
        print(f"price {price} USD")

if __name__ == "__main__":
    main()
