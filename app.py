from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import uuid
import time
import subprocess
from subprocess import TimeoutExpired

from AliceBobCindy import *

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'socraticalpaca'
Session(app)

N = 50
last_client_id = 0
session_states = {}


class SessionState:
    def __init__(self, client_id):
        self.client_id = client_id
        self.socrates = SocraticGPT(role="Socrates", n_round=N)
        self.question = None
        self.asked_question = False


@app.route('/')
def index():
    global last_client_id
    last_client_id += 1
    session['client_id'] = last_client_id
    session_states[last_client_id] = SessionState(last_client_id)
    return render_template('index.html')


@app.route('/active-message')
def active_message():

    global N, last_client_id, session_states

    client_id = int(session['client_id'])
    if client_id > last_client_id:
        print("current session id", client_id)
        print("last_client_id", last_client_id)
        last_client_id = client_id
        session_states[last_client_id] = SessionState(last_client_id)

    session_state = session_states[client_id]


    if session_state.question is None and not session_state.asked_question:
        session_state.asked_question = True
        msg = "What's your question?"
        return jsonify([{'role': 'system', 'response': msg}])

    return jsonify([])


@app.route('/chat', methods=['POST'])
def chat():
    global session_states
    client_id = int(session['client_id'])
    session_state = session_states[client_id]

    user_input = request.form['user_input'].strip()
    if not user_input:
        return jsonify([])

    if session_state.question is None:
        session_state.question = user_input
        session_state.socrates.set_question(session_state.question)
        session_state.socrates.update_history(user_input)
    else:
        session_state.socrates.update_history(user_input)

    response = session_state.socrates.get_response()
    return jsonify([{'role': 'socrates', 'response': response}])


if __name__ == '__main__':
    app.run(debug=True)