from flask import Flask, request, render_template_string, redirect
import requests
import os

# -----------------------------
# 1. Define Flask app variable
# -----------------------------
app = Flask(__name__)

# -----------------------------
# 2. Get environment variables
# -----------------------------
PASSWORD = os.environ.get("TRADING_APP_PASSWORD")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

# -----------------------------
# 3. HTML template
# -----------------------------
form_html = """
<!DOCTYPE html>
<html>
<head>
<title>Trade Submit</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="apple-touch-icon" href="{{ url_for('static', filename='icon.png') }}">
<link rel="shortcut icon" href="{{ url_for('static', filename='icon.png') }}">
<style>
body { font-family: Arial; padding: 20px; }
input, select, button { width: 100%; padding: 12px; margin-top: 8px; font-size: 16px; }
button { margin-top: 20px; }
</style>
</head>
<body>

{% if not authorized %}
<h2>Login</h2>
<form method="POST">
<input type="password" name="password" placeholder="Password" autofocus required>
<button>Login</button>
</form>

{% else %}
<h2>Submit Trade</h2>
<form method="POST">
<input name="ticker" placeholder="Ticker" required>
<select name="direction">
  <option>CALL</option>
  <option>PUT</option>
  <option>LONG</option>
  <option>SHORT</option>
</select>
<input name="expiration" placeholder="Expiration (MM/DD)" required>
<input name="price" placeholder="Price" required>
<input name="action" placeholder="Action (Entry/Add/Trim/Exit)" required>
<button>Submit</button>
</form>
{% endif %}

</body>
</html>
"""

# -----------------------------
# 4. Define routes
# -----------------------------
@app.route("/", methods=["GET","POST"])
def main():
    authorized = request.cookies.get("auth") == PASSWORD

    if request.method == "POST":
        if not authorized:
            if request.form.get("password") == PASSWORD:
                resp = redirect("/")
                resp.set_cookie("auth", PASSWORD)
                return resp
            return render_template_string(form_html, authorized=False)

        # send trade to Discord
        msg = f"**{request.form['ticker']} {request.form['direction']}**\n" \
              f"Exp: {request.form['expiration']}\n" \
              f"Price: {request.form['price']}\n" \
              f"Action: {request.form['action']}"
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": msg})
        except Exception as e:
            print("Error sending to Discord:", e)

        return redirect("/")

    return render_template_string(form_html, authorized=authorized)

# -----------------------------
# 5. Run app only if this file is main
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

