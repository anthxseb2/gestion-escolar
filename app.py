from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Hola, esta es mi primera web en Render 🚀"

if __name__ == "__main__":
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
