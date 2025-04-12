from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import subprocess
import signal
import platform

app = Flask(__name__)
DB = "database.db"
processes = {}

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS versioni (nome TEXT, link TEXT)")
        conn.commit()

@app.route("/")
def index():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM versioni")
        versioni = c.fetchall()
    return render_template("index.html", versioni=versioni)

@app.route("/aggiungi", methods=["GET", "POST"])
def aggiungi():
    if request.method == "POST":
        nome = request.form["nome"]
        link = request.form["link"]
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO versioni VALUES (?, ?)", (nome, link))
            conn.commit()
        return redirect(url_for("index"))
    return render_template("aggiungi.html")

@app.route("/server/<versione>", methods=["GET", "POST"])
def server(versione):
    base_dir = os.path.join(".", "server-file")
    percorso = os.path.join(base_dir, versione)
    jar_file = os.path.join(percorso, f"{versione}.jar")
    output = ""

    if request.method == "POST":
        azione = request.form["azione"]

        if azione == "scarica":
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT link FROM versioni WHERE nome = ?", (versione,))
                row = c.fetchone()
                if row:
                    link = row[0]
                    os.makedirs(percorso, exist_ok=True)
                    os.system(f"curl -L {link} -o \"{jar_file}\"")
                    with open(os.path.join(percorso, "eula.txt"), "w") as f:
                        f.write("eula=true")
                    output = f"Scaricato {versione}.jar"

        elif azione == "avvia":
            if versione in processes:
                output = "Server già avviato."
            else:
                try:
                    comando = ["java", "-Xmx1G", "-Xms1G", "-jar", f"{versione}.jar", "nogui"]
                    output += f"Esecuzione comando: {' '.join(comando)}\n"

                    proc = subprocess.Popen(
                        comando,
                        cwd=percorso,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                    )
                    processes[versione] = proc
                    output += "Server avviato."
                except Exception as e:
                    output = f"Errore avvio: {e}"

        elif azione == "stop":
            proc = processes.get(versione)
            if proc:
                try:
                    if platform.system() == "Windows":
                        proc.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        proc.terminate()
                    del processes[versione]
                    output = "Server arrestato."
                except Exception as e:
                    output = f"Errore arresto: {e}"
            else:
                output = "Nessun server in esecuzione."

        elif azione == "riavvia":
            if versione in processes:
                try:
                    processes[versione].terminate()
                    del processes[versione]
                except:
                    pass
            try:
                comando = ["java", "-Xmx1G", "-Xms1G", "-jar", f"{versione}.jar", "nogui"]
                output += f"Esecuzione comando: {' '.join(comando)}\n"

                proc = subprocess.Popen(
                    comando,
                    cwd=percorso,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0
                )
                processes[versione] = proc
                output += "Server riavviato."
            except Exception as e:
                output = f"Errore riavvio: {e}"

    return render_template("server.html", versione=versione, output=output)

@app.route("/elimina/<versione>", methods=["POST"])
def elimina(versione):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM versioni WHERE nome = ?", (versione,))
        conn.commit()

    cartella = os.path.join("server-file", versione)
    if os.path.exists(cartella):
        try:
            import shutil
            shutil.rmtree(cartella)
        except Exception as e:
            print(f"Errore durante l'eliminazione della cartella: {e}")

    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    os.makedirs("server-file", exist_ok=True)
    app.run(debug=True, port=5070)
