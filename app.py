from flask import Flask, render_template
import os

app = Flask(__name__, template_folder="templates")

@app.get("/")
def index():
	return render_template("index.html")

@app.get("/healthz")
def healthz():
	return {"status": "ok"}

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
