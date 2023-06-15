import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


@app.route("/")
def home():
    return 'API works!'


# Endpoint for adding two numbers
@app.route("/add", methods=["POST"])
async def add():
    data = await request.get_json()
    num1 = data["num1"]
    num2 = data["num2"]
    result = num1 + num2
    digits = data.get("digits", 2)
    result = round(result, digits)
    return {"result": result}


@app.route("/sub", methods=["POST"])
async def sub():
    data = await request.get_json()
    num1 = data["num1"]
    num2 = data["num2"]
    result = num1 - num2
    digits = data.get("digits", 2)
    result = round(result, digits)
    return {"result": result}


@app.route("/mul", methods=["POST"])
async def mul():
    data = await request.get_json()
    num1 = data["num1"]
    num2 = data["num2"]
    result = num1 * num2
    digits = data.get("digits", 2)
    result = round(result, digits)
    return {"result": result}


@app.route("/div", methods=["POST"])
async def div():
    data = await request.get_json()
    num1 = data["num1"]
    num2 = data["num2"]
    result = num1 / num2
    digits = data.get("digits", 2)
    result = round(result, digits)
    return {"result": result}


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5005)


if __name__ == "__main__":
    main()
