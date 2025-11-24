from flask import Flask, request, render_template_string, redirect
import requests
import os
PORT = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=PORT)

app = Flask(__name__)

PASSWORD = "dcdckc"
DISCORD_WEBHOOK = "YOUR_WEBHOOK_HERE"

form_html = """
<!DOCTYPE html>
<html>
<head>
<title>Trade Submit</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial; padding: 20px; }
input, select { width: 100%; padding: 12px; margin-top: 8px; }
button { width: 100%; padding: 14px; margin-top: 20px; font-size: 18px; }
</style>
</head>
<body>

<form method="POST">

{% if not authorized %}
<input type="password" name="password" placeholder="Password" autofocus>
<button>Login</button>
</form>
</body>
</html>
{% else %}
<input name="ticker" placeholder="Ticker">
<select name="direction">
  <option>CALL</option>
  <option>PUT</option>
  <option>LONG</option>
  <option>SHORT</option>
</select>
<input name="expiration" placeholder="Expiration (MM/DD)">
<input name="price" placeholder="Price">
<input name="action" placeholder="Action (Entry/Exit/etc)">
<button>Submit</button>
</form>

</body>
</html>
{% endif %}
"""

@app.route("/", methods=["GET","POST"])
def main():
    authorized = request.cookies.get("auth") == PASSWORD

    if request.method == "POST":
        if not authorized:
            if request.form.get("password") == PASSWORD:
                resp = redirect("/")
                resp.set_cookie("auth", PASSWORD)  # remembered login
                return resp
            return render_template_string(form_html, authorized=False)

        # send trade
        msg = f"**{request.form['ticker']} {request.form['direction']}**\n" \
              f"Exp: {request.form['expiration']}\n" \
              f"Price: {request.form['price']}\n" \
              f"Action: {request.form['action']}"

        requests.post(DISCORD_WEBHOOK, json={"content": msg})

        return redirect("/")

    return render_template_string(form_html, authorized=authorized)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
