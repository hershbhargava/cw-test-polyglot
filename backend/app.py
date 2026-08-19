from flask import Flask, jsonify

app = Flask(__name__)


def add(a, b):
    return a + b


@app.route("/api/sum/<int:a>/<int:b>")
def sum_route(a, b):
    return jsonify({"result": add(a, b)})


if __name__ == "__main__":
    app.run()
