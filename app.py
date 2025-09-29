from flask import Flask, render_template_string, request, redirect, url_for, session, flash, get_flashed_messages

app = Flask(__name__)
app.secret_key = "clave_super_segura"  # cámbiala en producción

# ---------------------
# Datos en memoria
# ---------------------
usuarios = {"admin": "1234"}

docentes = {}  # {codigo: {"nombre":..., "especialidad":..., "sueldo": float, "asistencias": int, "inasistencias": int, "tardanzas": int}}
alumnos = {}   # {codigo: {"nombre":..., "grado":..., "pagos": [float]}}

# ---------------------
# Plantilla base
# ---------------------
def base_html(contenido_html):
    template = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Gestión Escolar Fray Martincito</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
      <div class="container py-4">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="text-center mb-3">
              <img src="{{ url_for('static', filename='fraymartincito.png') }}" alt="Logo" style="max-height:100px;" class="mb-2"><br>
              <h1 class="h4 mb-0">📘 Gestión Escolar Fray Martincito</h1>
              {% if session.get('usuario') %}
                <div class="small text-muted">
                  Conectado como <strong>{{ session['usuario'] }}</strong> — 
                  <a href="{{ url_for('logout') }}">Cerrar sesión</a>
                </div>
              {% endif %}
            </div>
            <hr>
            {% for category, msg in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ msg }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
            {% endfor %}
            <div>
              {{ contenido|safe }}
            </div>
          </div>
        </div>
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    messages = get_flashed_messages(with_categories=True)
    return render_template_string(template, contenido=contenido_html, messages=messages)

# ---------------------
# Login / Logout
# ---------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("menu"))

    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")
        if usuarios.get(usuario) == clave:
            session["usuario"] = usuario
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("menu"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")

    form = """
      <h4>🔐 Iniciar sesión</h4>
      <form method="post" class="row g-2">
        <div class="col-12"><input class="form-control" name="usuario" placeholder="Usuario" required></div>
        <div class="col-12"><input class="form-control" type="password" name="clave" placeholder="Contraseña" required></div>
        <div class="col-12"><button class="btn btn-primary w-100">Ingresar</button></div>
      </form>
    """
    return base_html(form)

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Cerraste sesión.", "success")
    return redirect(url_for("login"))

# ---------------------
# Menú principal
# ---------------------
@app.route("/menu")
def menu():
    if "usuario" not in session:
        return redirect(url_for("login"))

    contenido = """
      <h4>🏠 Menú principal</h4>
      <div class="list-group">
        <a href="/gestionar_docentes" class="list-group-item list-group-item-action">👩‍🏫 Gestión de Docentes</a>
        <a href="/gestionar_alumnos" class="list-group-item list-group-item-action">👨‍🎓 Registro de Pagos de Alumnos</a>
      </div>
    """
    return base_html(contenido)

# ---------------------
# Gestión de Docentes
# ---------------------
@app.route("/gestionar_docentes", methods=["GET", "POST"])
def gestionar_docentes():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("action") == "registrar_docente":
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        especialidad = request.form.get("especialidad")
        sueldo = float(request.form.get("sueldo") or 0)
        if codigo not in docentes:
            docentes[codigo] = {"nombre": nombre, "especialidad": especialidad, "sueldo": sueldo,
                                "asistencias": 0, "inasistencias": 0, "tardanzas": 0}
            flash(f"Docente {nombre} registrado.", "success")
        else:
            flash("Ese código ya está registrado.", "warning")
        return redirect(url_for("gestionar_docentes"))

    filas = ""
    if docentes:
        for c, d in docentes.items():
            pago_total = d["sueldo"] + d["asistencias"] * 100 - d["inasistencias"] * 10 - d["tardanzas"]
            filas += f"""
            <tr>
              <td>{c}</td>
              <td>{d['nombre']}</td>
              <td>{d['especialidad']}</td>
              <td>{d['sueldo']:.2f}</td>
              <td>{d['asistencias']}</td>
              <td>{d['inasistencias']}</td>
              <td>{d['tardanzas']}</td>
              <td>{pago_total:.2f}</td>
              <td>
                <a href="/docentes/calcular/{c}" class="btn btn-sm btn-outline-primary">Calcular Pago</a>
              </td>
            </tr>
            """
    else:
        filas = "<tr><td colspan='9' class='text-center'>No hay docentes registrados.</td></tr>"

    contenido = f"""
      <h4>👩‍🏫 Registrar docente</h4>
      <form method="post" class="row g-2 mb-3">
        <input type="hidden" name="action" value="registrar_docente">
        <div class="col-md-2"><input class="form-control" name="codigo" placeholder="Código" required></div>
        <div class="col-md-3"><input class="form-control" name="nombre" placeholder="Nombre" required></div>
        <div class="col-md-3"><input class="form-control" name="especialidad" placeholder="Especialidad" required></div>
        <div class="col-md-2"><input class="form-control" type="number" step="0.01" name="sueldo" placeholder="Sueldo base" required></div>
        <div class="col-md-2"><button class="btn btn-success w-100">Agregar</button></div>
      </form>

      <h5>📋 Lista de Docentes</h5>
      <table class="table table-striped">
        <thead><tr><th>Código</th><th>Nombre</th><th>Especialidad</th><th>Sueldo</th><th>Asistencias</th><th>Inasistencias</th><th>Tardanzas (min)</th><th>Pago Total</th><th>Acción</th></tr></thead>
        <tbody>{filas}</tbody>
      </table>

      <h5>Registrar asistencia, falta o tardanza</h5>
      <form method="post" action="/docentes/asistencia" class="row g-2 mb-2">
        <div class="col-md-4"><input class="form-control" name="codigo" placeholder="Código del docente" required></div>
        <div class="col-md-2"><button class="btn btn-success w-100">Asistencia</button></div>
      </form>

      <form method="post" action="/docentes/inasistencia" class="row g-2 mb-2">
        <div class="col-md-4"><input class="form-control" name="codigo" placeholder="Código del docente" required></div>
        <div class="col-md-2"><button class="btn btn-danger w-100">Inasistencia</button></div>
      </form>

      <form method="post" action="/docentes/tardanza" class="row g-2">
        <div class="col-md-3"><input class="form-control" name="codigo" placeholder="Código del docente" required></div>
        <div class="col-md-3"><input class="form-control" type="number" name="minutos" placeholder="Minutos tarde" required></div>
        <div class="col-md-2"><button class="btn btn-info w-100">Tardanza</button></div>
      </form>

      <a href="/menu" class="btn btn-secondary mt-3">⬅ Volver al menú</a>
    """
    return base_html(contenido)

@app.route("/docentes/calcular/<codigo>")
def calcular_pago_docente(codigo):
    if codigo not in docentes:
        flash("Docente no encontrado.", "danger")
    else:
        d = docentes[codigo]
        pago_total = d["sueldo"] + d["asistencias"] * 100 - d["inasistencias"] * 10 - d["tardanzas"]
        flash(f"El pago total de {d['nombre']} es: S/ {pago_total:.2f}", "info")
    return redirect(url_for("gestionar_docentes"))

@app.route("/docentes/asistencia", methods=["POST"])
def docentes_asistencia():
    codigo = request.form.get("codigo")
    if codigo in docentes:
        docentes[codigo]["asistencias"] += 1
        flash(f"Asistencia registrada para {docentes[codigo]['nombre']}", "success")
    else:
        flash("Docente no encontrado.", "danger")
    return redirect(url_for("gestionar_docentes"))

@app.route("/docentes/inasistencia", methods=["POST"])
def docentes_inasistencia():
    codigo = request.form.get("codigo")
    if codigo in docentes:
        docentes[codigo]["inasistencias"] += 1
        flash(f"Inasistencia registrada para {docentes[codigo]['nombre']}", "warning")
    else:
        flash("Docente no encontrado.", "danger")
    return redirect(url_for("gestionar_docentes"))

@app.route("/docentes/tardanza", methods=["POST"])
def docentes_tardanza():
    codigo = request.form.get("codigo")
    minutos = int(request.form.get("minutos") or 0)
    if codigo in docentes:
        docentes[codigo]["tardanzas"] += minutos
        flash(f"Tardanza registrada ({minutos} min) para {docentes[codigo]['nombre']}", "info")
    else:
        flash("Docente no encontrado.", "danger")
    return redirect(url_for("gestionar_docentes"))

# ---------------------
# Gestión de Alumnos
# ---------------------
@app.route("/gestionar_alumnos", methods=["GET", "POST"])
def gestionar_alumnos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("action") == "registrar_alumno":
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        grado = request.form.get("grado")
        if codigo not in alumnos:
            alumnos[codigo] = {"nombre": nombre, "grado": grado, "pagos": []}
            flash(f"Alumno {nombre} registrado.", "success")
        else:
            flash("Ese código de alumno ya existe.", "warning")
        return redirect(url_for("gestionar_alumnos"))

    filas = ""
    if alumnos:
        for c, a in alumnos.items():
            total_pagado = sum(a["pagos"])
            filas += f"""
            <tr>
              <td>{c}</td>
              <td>{a['nombre']}</td>
              <td>{a['grado']}</td>
              <td>{total_pagado:.2f}</td>
              <td><a href="/alumnos/pagos/{c}" class="btn btn-sm btn-outline-primary">Ver Pagos</a></td>
            </tr>
            """
    else:
        filas = "<tr><td colspan='5' class='text-center'>No hay alumnos registrados.</td></tr>"

    contenido = f"""
      <h4>👨‍🎓 Registrar alumno</h4>
      <form method="post" class="row g-2 mb-3">
        <input type="hidden" name="action" value="registrar_alumno">
        <div class="col-md-2"><input class="form-control" name="codigo" placeholder="Código" required></div>
        <div class="col-md-4"><input class="form-control" name="nombre" placeholder="Nombre" required></div>
        <div class="col-md-3"><input class="form-control" name="grado" placeholder="Grado" required></div>
        <div class="col-md-3"><button class="btn btn-success w-100">Agregar</button></div>
      </form>

      <h5>📋 Lista de Alumnos</h5>
      <table class="table table-striped">
        <thead><tr><th>Código</th><th>Nombre</th><th>Grado</th><th>Total Pagado</th><th>Acciones</th></tr></thead>
        <tbody>{filas}</tbody>
      </table>

      <a href="/menu" class="btn btn-secondary mt-3">⬅ Volver al menú</a>
    """
    return base_html(contenido)

@app.route("/alumnos/pagos/<codigo>", methods=["GET", "POST"])
def pagos_alumno(codigo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    if codigo not in alumnos:
        flash("Alumno no encontrado.", "danger")
        return redirect(url_for("gestionar_alumnos"))

    alumno = alumnos[codigo]

    if request.method == "POST":
        monto = float(request.form.get("monto") or 0)
        alumno["pagos"].append(monto)
        flash(f"Pago de S/ {monto:.2f} registrado para {alumno['nombre']}", "success")
        return redirect(url_for("pagos_alumno", codigo=codigo))

    lista_pagos = "".join([f"<li>S/ {p:.2f}</li>" for p in alumno["pagos"]]) or "<li>No hay pagos aún</li>"

    contenido = f"""
      <h4>💰 Pagos de {alumno['nombre']} ({alumno['grado']})</h4>
      <form method="post" class="row g-2 mb-3">
        <div class="col-md-4"><input class="form-control" type="number" step="0.01" name="monto" placeholder="Monto" required></div>
        <div class="col-md-2"><button class="btn btn-success w-100">Registrar Pago</button></div>
      </form>

      <h5>Historial de pagos</h5>
      <ul>{lista_pagos}</ul>

      <a href="/gestionar_alumnos" class="btn btn-secondary mt-3">⬅ Volver</a>
    """
    return base_html(contenido)

# ---------------------
# Ejecutar servidor
# ---------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render usa la variable PORT
    app.run(host="0.0.0.0", port=port, debug=True)
