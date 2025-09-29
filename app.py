import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "¡Hola! 🚀 Tu app Flask está corriendo en Render."

if __name__ == "__main__":
    # Render necesita que escuche en el puerto que él asigna
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
