from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>¡Hola mundo desde Flask en Render 🚀!</h1>"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
