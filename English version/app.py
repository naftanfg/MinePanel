from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import subprocess
import signal
import platform
import shutil

app = Flask(__name__)
DB = "database.db"
processes = {}

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS versions (name TEXT, link TEXT)")
        conn.commit()

@app.route("/")
def index():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM versions")
        versions = c.fetchall()
    return render_template("index.html", versions=versions)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        link = request.form["link"]
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO versions VALUES (?, ?)", (name, link))
            conn.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/server/<version>", methods=["GET", "POST"])
def server(version):
    base_dir = os.path.join(".", "server-files")
    path = os.path.join(base_dir, version)
    jar_file = os.path.join(path, f"{version}.jar")
    output = ""

    if request.method == "POST":
        action = request.form["action"]

        if action == "download":
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT link FROM versions WHERE name = ?", (version,))
                row = c.fetchone()
                if row:
                    link = row[0]
                    os.makedirs(path, exist_ok=True)
                    os.system(f"curl -L {link} -o \"{jar_file}\"")
                    with open(os.path.join(path, "eula.txt"), "w") as f:
                        f.write("eula=true")
                    output = f"Downloaded {version}.jar"

        elif action == "start":
            if version in processes:
                output = "Server already running."
            else:
                try:
                    command = ["java", "-Xmx1G", "-Xms1G", "-jar", f"{version}.jar", "nogui"]
                    output += f"Running command: {' '.join(command)}\n"

                    proc = subprocess.Popen(
                        command,
                        cwd=path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                    )
                    processes[version] = proc
                    output += "Server started."
                except Exception as e:
                    output = f"Start error: {e}"

        elif action == "stop":
            proc = processes.get(version)
            if proc:
                try:
                    if platform.system() == "Windows":
                        proc.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        proc.terminate()
                    del processes[version]
                    output = "Server stopped."
                except Exception as e:
                    output = f"Stop error: {e}"
            else:
                output = "No running server."

        elif action == "restart":
            if version in processes:
                try:
                    processes[version].terminate()
                    del processes[version]
                except:
                    pass
            try:
                command = ["java", "-Xmx1G", "-Xms1G", "-jar", f"{version}.jar", "nogui"]
                output += f"Running command: {' '.join(command)}\n"

                proc = subprocess.Popen(
                    command,
                    cwd=path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                )
                processes[version] = proc
                output += "Server restarted."
            except Exception as e:
                output = f"Restart error: {e}"

    return render_template("server.html", version=version, output=output)

@app.route("/delete/<version>", methods=["POST"])
def delete(version):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM versions WHERE name = ?", (version,))
        conn.commit()

    folder = os.path.join("server-files", version)
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print(f"Error deleting folder: {e}")

    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    os.makedirs("server-files", exist_ok=True)
    app.run(debug=False, port=5060)
