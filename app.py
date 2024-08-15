from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template
import cryptocode
import os
import pip
from requests_oauthlib import OAuth2Session
OAUTH2_CLIENT_ID = ""
OAUTH2_CLIENT_SECRET = "iitbhunt"
OAUTH2_REDIRECT_URI = 'https://dcrypt.ml/callback'
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')

import sqlite3
import gspread

gc = gspread.service_account(filename='service_account.json')

sh = gc.open("TREASURE HUNT (Responses)")
worksheet = sh.sheet1

AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)

conn = sqlite3.connect('sql.db')
cur = conn.cursor()
cur.execute(
    "CREATE table IF NOT EXISTS users (username VARCHAR, level VARCHAR)"
)
conn.commit()
cur.execute(
    "CREATE table IF NOT EXISTS quests (context VARCHAR, answer VARCHAR, level VARCHAR)"
)
conn.commit()

conn.close()



@app.route("/guide")
def guide():
    return render_template("guidelines.html")





@app.route("/")
def indexx():
    if not session.get('username'):
        return render_template("guidelines.html", authentic=0, reg=1)
    else:

        conn = sqlite3.connect('sql.db')
        cur = conn.cursor()
        result = cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (session.get('username'),)).fetchone()
        if not result:
            cur.execute("INSERT INTO users(username,level) VALUES (?,0)", (session.get('username'),))
            conn.commit()
        return redirect(url_for('.play'))

@app.route('/auth')
def auth():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def reg():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cell = worksheet.find(username)

        if cell:
            cell = cell.row
            cpassword = worksheet.acell(f'I{cell}').value
            if password == cpassword:
                session['username'] = username
                return redirect(url_for('.play'))
            else:
                return render_template('login.html',error="Incorrect Credentials")
        else:
            return render_template('login.html',error="Incorrect Credentials")



@app.route("/play", methods=["POST", "GET"])
def play():
    if request.method == "POST":
        ans = request.form.get("answer")
        lvl = session.get('level')
        conn =  sqlite3.connect('sql.db')
        cur = conn.cursor()
        cur.execute(
            "SELECT level from users WHERE username = ?", (session.get('username'),)
        )
        data = cur.fetchone()

        cur.execute(
            "SELECT context, answer from quests WHERE level = ?", (data[0],)
        )
        question = cur.fetchone()
        print(ans.lower(), question[1])
        ans.replace(" ", "")
        if ans.lower() == question[1]:
            cur.execute(
                "SELECT level from users WHERE username = ?", (session.get('username'),)
            )
            data = cur.fetchone()

            cur.execute(
                "UPDATE users SET level = ? WHERE username = ?", (int(data[0])+1, session.get('username'),)
            )
            conn.commit()
            cur.execute(
                "SELECT level from users WHERE username = ?", (session.get('username'),)
            )
            data = cur.fetchone()

            cur.execute(
            "SELECT context, answer from quests WHERE level = ?", (data[0],)
        )
            question = cur.fetchone()


            return render_template("play.html", ans=1, dataa = data, quest= question)
        else:
            return render_template("play.html", ans=0, dataa = data, quest= question)
    else:
        if not session.get('username'):
            return redirect(url_for('.indexx'))
        conn =  sqlite3.connect('sql.db')
        cur = conn.cursor()
        cur.execute(
            "SELECT level from users WHERE username = ?", (session.get('username'),)
        )
        data = cur.fetchone()

        if not data:
            return redirect(url_for('.indexx'))
        cur.execute(
            "SELECT context, answer from quests WHERE level = ?", (data[0],)
        )
        question = cur.fetchone()

        return render_template("play.html", dataa = data, quest= question)


if __name__ == "__main__":
    app.run()
