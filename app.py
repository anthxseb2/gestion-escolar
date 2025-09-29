from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Bienvenido al Proyecto de Gestión Escolar</h1><p>Esta es una web básica con Flask 🚀</p>"

if __name__ == "__main__":
    app.run(debug=True)
