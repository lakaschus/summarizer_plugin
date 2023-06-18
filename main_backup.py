import quart
import quart_cors
from quart import request
from web_scraping import get_content
import summarizer

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


@app.route("/")
def home():
    return 'API works!'


# Endpoint for adding two numbers
@app.route("/summary", methods=["POST"])
async def add():
    data = await request.get_json()
    url = data["url"]
    print("URL: ", url)
    content = get_content(url)
    sum = summarizer.GPTSummarizer(content)
    summary = sum.summarize_large_text()
    print("Summary: ", summary)
    return {"result": summary}


@app.get("/logo.png")
async def plugin_logo():
    filename = 'res/logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open("./.well-known/openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
