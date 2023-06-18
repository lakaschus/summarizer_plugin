import quart
import quart_cors
import threading
import time
from quart import Quart, jsonify, Response
from quart import request
from web_scraping import get_content
import summarizer

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

@app.route("/") 
def home():
    return 'API works!'

results = {}

def long_running_task(url, task_id):
    print("URL: ", url)
    content = get_content(url)
    sum = summarizer.GPTSummarizer(content)
    summary = sum.summarize_large_text()
    results[task_id] = summary

@app.route("/summary", methods=["POST"])
async def add():
    data = await request.get_json()
    url = data["url"]
    task_id = str(time.time())  # Generate a unique task ID
    threading.Thread(target=long_running_task, args=(url, task_id)).start()
    return jsonify({"task_id": task_id}), 202

@app.route("/summary/<task_id>", methods=["GET"])
async def get_result(task_id):
    if task_id in results:
        summary = results[task_id]
        del results[task_id]
        return jsonify({"summary": summary})
    else:
        return jsonify({"status": "Processing..."}), 202


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
