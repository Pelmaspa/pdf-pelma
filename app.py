
import os
import asyncio
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/modulo_visitatori')
def modulo_visitatori():
    return render_template('modulo_visitatori.html')

@app.route('/modulo_autisti')
def modulo_autisti():
    return render_template('modulo_autisti.html')

@app.route('/healthz')
def healthz():
    return "ok", 200

@app.route('/send_pdf', methods=['POST'])
def send_pdf():
    try:
        data = request.get_json(force=True)
        html = data.get('html', '')
        subject = data.get('subject', 'Modulo compilato')
        filename = data.get('filename', f"modulo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

        if not html or '<html' not in html.lower():
            return jsonify({'success': False, 'error': 'HTML non valido o mancante'}), 400

        # Fresh event loop per thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            pdf_bytes = loop.run_until_complete(html_to_pdf(html))
        finally:
            loop.close()

        # Email
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = 'pelma.aziendale1@gmail.com'
        msg['To'] = 'francesca.podesta@pelma.it'
        msg.set_content('In allegato il PDF completo del modulo, firme incluse.')
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=filename)

        gmail_user = 'pelma.aziendale1@gmail.com'
        gmail_pass = os.environ.get('GMAIL_APP_PASSWORD')
        if not gmail_pass:
            return jsonify({'success': False, 'error': 'Variabile GMAIL_APP_PASSWORD non impostata sul server'}), 500

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)

        return jsonify({'success': True})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

async def html_to_pdf(html: str) -> bytes:
    from pyppeteer import launch
    executable_path = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    launch_kwargs = {
        "handleSIGINT": False,
        "handleSIGTERM": False,
        "handleSIGHUP": False,
        "args": ["--no-sandbox","--disable-web-security","--disable-dev-shm-usage"]
    }
    if executable_path:
        launch_kwargs["executablePath"] = executable_path

    browser = await launch(**launch_kwargs)
    try:
        page = await browser.newPage()
        # Some pyppeteer builds don't support waitUntil kw; and no waitForTimeout either. Use a tiny async sleep.
        await page.setContent(html)
        await asyncio.sleep(0.4)  # let layout settle
        pdf = await page.pdf({
            'format': 'A4',
            'printBackground': True,
            'margin': {'top':'12mm','right':'12mm','bottom':'12mm','left':'12mm'}
        })
        return pdf
    finally:
        await browser.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
