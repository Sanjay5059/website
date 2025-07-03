from flask import Flask, request, Response, stream_with_context, render_template
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_API_URL = "http://localhost:11434/api/chat"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/employee/leave')
def leave_form():
    return render_template('employee/leave.html')

@app.route('/employee/timesheet')
def timesheet():
    return render_template('employee/timesheet.html')

@app.route('/employee/compoff')
def compoff():
    return render_template('employee/compoff.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/hr/onboarding')
def onboarding():
    return render_template('hr/onboarding.html')

@app.route('/hr/induction')
def induction():
    return render_template('hr/induction.html')

@app.route('/tickets')
def tickets():
    return render_template('tickets/index.html')

@app.route('/it-helpdesk')
def it_helpdesk():
    return render_template('it/helpdesk.html')

@app.route('/knowledge')
def knowledge():
    return render_template('knowledge/index.html')

@app.route('/jobs')
def jobs():
    return render_template('jobs/index.html')

@app.route('/employee-portal')
def employee_portal():
    return render_template('portal/employee_portal.html')

@app.route('/reports')
def reports():
    return render_template('reports/index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_prompt = data.get("prompt")
    print(f"[Flask] Prompt received: {user_prompt}")

    def generate():
        payload = {
            "model": "llama3",
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": True
        }

        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    line_json = json.loads(line.decode('utf-8'))
                    chunk = line_json.get('message', {}).get('content', '')
                    yield chunk

    return Response(stream_with_context(generate()), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
