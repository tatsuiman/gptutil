import os
import sys
import requests
import click
import openai

PRICE_PER_IMAGE = {
    "1024x1024": 0.020,
    "512x512": 0.018,
    "256x256": 0.016,
}


@click.command()
@click.option("--prompt", "-p", default="", help="Prompt to generate image.")
@click.option("-v", "--verbose", is_flag=True, help="Show Image URL and cost.")
@click.option(
    "--size",
    "-s",
    type=click.Choice(["1024x1024", "512x512", "256x256"], case_sensitive=False),
    default="256x256",
    help="Image resolution.",
)
@click.option("--n", type=int, default=1, help="Number of images to generate (1-10).")
@click.argument("output", type=click.Path())
def main(prompt, verbose, size, n, output):
    if n < 1 or n > 10:
        print("画像の枚数は1から10の範囲で指定してください。")
        return

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("環境変数にOpenAI API キーが設定されていません。")
        return

    if not sys.stdin.isatty():
        content = sys.stdin.read()
        prompt = f"{prompt}\n{content}"

    response = openai.Image.create(prompt=prompt, n=n, size=size)

    image_data = response["data"]
    for i, data in enumerate(image_data):
        image_url = data["url"]
        if verbose:
            print(f"Image {i + 1} URL: {image_url}")

        output_file = f"{os.path.splitext(output)[0]}_{i + 1}{os.path.splitext(output)[1]}"
        save_image_from_url(image_url, output_file)
        print(f"画像 {i + 1} が {output_file} に保存されました。")

    if verbose:
        cost_per_image = PRICE_PER_IMAGE[size]
        total_cost = cost_per_image * n
        print(f"合計コスト: ${total_cost:.2f}")


def save_image_from_url(url, file_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


if __name__ == "__main__":
    main()
