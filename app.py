from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hola, esta es mi primera web en Render 🚀"

if __name__ == "__main__":
    # Render usa el puerto de la variable de entorno PORT
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
