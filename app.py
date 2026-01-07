from flask import Flask, render_template, request, redirect, url_for
import psycopg2, os
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change-this"

# PostgreSQL (ENV)
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=os.getenv("DB_PORT"),
    sslmode="require"
)

# Cloudinary (ENV)
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API_KEY"),
    api_secret=os.getenv("CLOUD_API_SECRET")
)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        file = request.files["profile"]
        upload = cloudinary.uploader.upload(file)
        image_url = upload["secure_url"]

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(username, image) VALUES(%s,%s)",
            (request.form["username"], image_url)
        )
        conn.commit()

        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    cur = conn.cursor()
    cur.execute("SELECT username, image FROM users ORDER BY id DESC LIMIT 1")
    user = cur.fetchone()
    return render_template("dashboard.html", user=user)

app.run()
