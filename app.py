import os
import smtplib
import base64
from flask import Flask, render_template, request, jsonify
from email.message import EmailMessage
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/modulo_visitatori")
def modulo_visitatori():
    return render_template("modulo_visitatori.html")

@app.route("/modulo_autisti")
def modulo_autisti():
    return render_template("modulo_autisti.html")

@app.route("/invia_modulo", methods=["POST"])
def invia_modulo():
    try:
        data = request.get_json()
        print("DEBUG - JSON ricevuto:", data)

        form_data = data.get("formData", {})
        firma1 = data.get("firma1", "")
        firma2 = data.get("firma2", "")
        modulo = data.get("modulo", "modulo")

        # Se form_data è vuoto, restituisco errore chiaro
        if not form_data:
            return jsonify({"errore": "Chiave 'formData' mancante nel JSON ricevuto"}), 400

        # Crea PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Modulo: {modulo} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)

        for k, v in form_data.items():
            pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)

        msg = EmailMessage()
        msg["Subject"] = f"Modulo {modulo} compilato"
        msg["From"] = "pelma.aziendale1@gmail.com"
        msg["To"] = "francesca.podesta@pelma.it"
        msg.set_content("In allegato il modulo compilato.")

        msg.add_attachment(buffer.read(), maintype="application", subtype="pdf", filename=f"{modulo}.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("pelma.aziendale1@gmail.com", os.environ["GMAIL_APP_PASSWORD"])
            smtp.send_message(msg)

        return jsonify({"esito": "ok"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"errore": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)