from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Otázky pro hru
questions = [
    {"q": "Jaké zvíře tahá Santovy sáně?", "type": "mc", "options": ["A) Sob", "B) Kůň", "C) Pes"], "a": "A", "clue": "Další QR kód najdeš u lednice ve škole."},
    {"q": "Co nosí Ježíšek?", "type": "text", "a": "dárky", "clue": "Další QR kód najdeš u šatny."},
    {"q": "Kolik je na adventním věnci svíček?", "type": "mc", "options": ["A) 3", "B) 4", "C) 5"], "a": "B", "clue": "Teď běž do učebny 32 – tam najdeš obálku!"}
]

# HTML šablona s QR skenem
template = '''
<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<title>Vánoční QR Quest</title>
<style>
body { background-color: #ffe6e6; font-family: Arial, sans-serif; text-align: center; padding: 50px; }
input { padding: 10px; font-size: 16px; margin: 5px; }
button { padding: 10px 20px; font-size: 16px; background-color: #008000; color: white; border: none; border-radius: 10px; cursor: pointer; margin: 5px; }
button:hover { background-color: #005500; }
</style>
</head>
<body>
<h1>🎄 Vánoční QR Quest 🎅</h1>
{% if stage is none %}
  <form method="post">
    <p>Zadej název týmu:</p>
    <input type="text" name="team_name" required>
    <p>Zadej členy týmu (oddělené čárkou):</p>
    <input type="text" name="members" required>
    <br>
    <button type="submit">Začít hru</button>
  </form>
{% elif qr_scanned == False %}
  <p>Tým: {{ team }}</p>
  <p>Členové: {{ members }}</p>
  <p>⏱ Čas: {{ elapsed }}</p>
  <h2>Indicie: {{ clue }}</h2>
  <p>Naskenuj QR kód pro otázku:</p>
  <div id="qr-reader" style="width:300px; margin:auto"></div>
  <script src="https://unpkg.com/html5-qrcode"></script>
  <script>
  function onScanSuccess(decodedText, decodedResult) {
      window.location.href = '/scan';
  }
  var html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: 250 });
  html5QrcodeScanner.render(onScanSuccess);
  </script>
{% else %}
  <p>Tým: {{ team }}</p>
  <p>Členové: {{ members }}</p>
  <p>⏱ Čas: {{ elapsed }}</p>
  <h2>{{ question.q }}</h2>
  {% if question.type == 'mc' %}
    {% for option in question.options %}
      <form method="post" style="display:inline-block;">
        <input type="hidden" name="answer" value="{{ option[0] }}">
        <button type="submit">{{ option }}</button>
      </form>
    {% endfor %}
  {% elif question.type == 'text' %}
    <form method="post">
      <input type="text" name="answer" required>
      <br>
      <button type="submit">Odpovědět</button>
    </form>
  {% endif %}
  {% if clue %}
    <p style="margin-top:20px; font-weight:bold;">Další indicie: {{ clue }}</p>
  {% endif %}
{% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['team_name'] = request.form.get('team_name')
        session['members'] = request.form.get('members')
        session['start_time'] = datetime.now().isoformat()
        session['stage'] = 0
        session['qr_scanned'] = False
        session['clue'] = "První indicie: Jděte k hlavnímu vchodu školy."  # první indicie
        return redirect(url_for('game'))
    return render_template_string(template, stage=None)

@app.route('/game', methods=['GET', 'POST'])
def game():
    team = session.get('team_name')
    members = session.get('members')
    start_time = datetime.fromisoformat(session.get('start_time'))
    stage = session.get('stage')
    qr_scanned = session.get('qr_scanned')
    clue = session.get('clue')

    elapsed_time = datetime.now() - start_time
    minutes = elapsed_time.seconds // 60
    seconds = elapsed_time.seconds % 60
    elapsed = f"{minutes}:{seconds:02d}"

    if qr_scanned and stage < len(questions):
        question = questions[stage]
        if request.method == 'POST':
            answer = request.form.get('answer', '').strip().upper()
            correct = question['a'].upper()
            if answer == correct:
                session['stage'] = stage + 1
                session['qr_scanned'] = False
                session['clue'] = question['clue'] if stage + 1 <= len(questions) else "Konec hry. Najděte obálku."
                return redirect(url_for('game'))
            else:
                return f'<p>Špatná odpověď! Zkus to znovu.</p><a href="{url_for("game")}">Zpět</a>'
    else:
        question = None

    return render_template_string(template, stage=stage, total=len(questions), team=team, members=members, elapsed=elapsed, qr_scanned=qr_scanned, question=question, clue=clue)

@app.route('/scan')
def scan():
    # Po naskenování QR nastavíme, že otázka se má zobrazit
    session['qr_scanned'] = True
    return redirect(url_for('game'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)