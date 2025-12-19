from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
app.secret_key = "demo_secret_key"

# -------------------------
# DEMO LOGIN
# -------------------------
USERNAME = "admin"
PASSWORD = "demo123"

# -------------------------
# GOOGLE SHEET
# -------------------------
SHEET_ID = "1yBnfIni5qAjMM0_g90oxR2jXTgUlI98oaRz7Kz0g4sg"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# -------------------------
# LOAD DATA
# -------------------------
def load_data():
    df = pd.read_csv(SHEET_URL)
    df["AMC_End_Date"] = pd.to_datetime(df["AMC_End_Date"], dayfirst=True)
    return df

# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    df = load_data()
    today = datetime.today()

    df["Days_Remaining"] = (df["AMC_End_Date"] - today).dt.days

    total_clients = len(df)
    expired = len(df[df["Days_Remaining"] < 0])
    expiring_soon = len(df[(df["Days_Remaining"] >= 0) & (df["Days_Remaining"] <= 30)])
    active = len(df[df["Days_Remaining"] > 30])

    upcoming = df[(df["Days_Remaining"] >= 0) & (df["Days_Remaining"] <= 30)]
    upcoming = upcoming.sort_values("Days_Remaining")

    return render_template(
        "dashboard.html",
        total_clients=total_clients,
        active=active,
        expiring_soon=expiring_soon,
        expired=expired,
        upcoming=upcoming.to_dict("records")
    )

# -------------------------
# WHATSAPP DEMO
# -------------------------
@app.route("/send_whatsapp/<client_name>")
def send_whatsapp(client_name):
    flash(f"WhatsApp reminder sent successfully to {client_name}")
    return redirect(url_for("dashboard"))

# -------------------------
# INVOICE PDF GENERATION
# -------------------------
@app.route("/generate_invoice/<client_name>")
def generate_invoice(client_name):
    df = load_data()
    client = df[df["Client_Name"] == client_name].iloc[0]

    file_name = f"Invoice_{client_name.replace(' ', '_')}.pdf"
    file_path = os.path.join(file_name)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Fire Service Invoice")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Client Name: {client['Client_Name']}")
    c.drawString(50, height - 130, f"Service Type: {client['Service_Type']}")
    c.drawString(50, height - 160, f"AMC End Date: {client['AMC_End_Date'].date()}")
    c.drawString(50, height - 190, f"Invoice Amount: ₹ {client['Invoice_Amount']}")

    c.drawString(50, height - 240, "Thank you for your business!")

    c.showPage()
    c.save()

    return send_file(file_path, as_attachment=True)

# -------------------------
# RUN APP
# -------------------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

