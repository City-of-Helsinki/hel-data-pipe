from flask import Flask

app = Flask(__name__)


@app.route("/")
def testing():
    return "Testing"


@app.route("/readiness")
def readiness():
    return "OK"


@app.route("/healthz")
def healthz():
    return "OK"


if __name__ == "__main__":
    app.run()
