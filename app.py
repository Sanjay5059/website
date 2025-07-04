from flask import Flask, request, Response, stream_with_context, render_template, redirect, url_for, session
import requests, json
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = '2169ae279691918b3b5c54641f2efb9e17de8ac4e4722e376ea6475085828918'
CORS(app)

# 🔐 OAuth Setup
oauth = OAuth(app)

# Google OAuth
oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID',
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={'access_type': 'offline', 'prompt': 'consent'},
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# Microsoft OAuth
oauth.register(
    name='microsoft',
    client_id='YOUR_MICROSOFT_CLIENT_ID',
    client_secret='YOUR_MICROSOFT_CLIENT_SECRET',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    api_base_url='https://graph.microsoft.com/v1.0/',
    client_kwargs={'scope': 'User.Read openid email profile'},
)

# 🔁 Auth Routes
@app.route('/login/<provider>')
def login(provider):
    redirect_uri = url_for('authorize', provider=provider, _external=True)
    return oauth.create_client(provider).authorize_redirect(redirect_uri)

@app.route('/authorize/<provider>')
def authorize(provider):
    client = oauth.create_client(provider)
    token = client.authorize_access_token()
    user_info = client.parse_id_token(token)
    email = user_info.get('email')
    domain = email.split('@')[-1]

    if domain != 'yourcompany.com':  # ✅ Replace this with your domain
        return "Unauthorized", 403

    session['user'] = {
        'email': email,
        'name': user_info.get('name'),
        'role': 'employee'
    }
    session['user_role'] = 'employee'
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# 📄 Routes
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

@app.route('/signin', methods=['GET'])
def signin():
    return render_template('signin.html')

@app.route('/readmore')
def read_more():
    return render_template('readmore.html')




# 🤖 Chatbot Integration
OLLAMA_API_URL = "http://localhost:11434/api/chat"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_prompt = data.get("prompt")

    def generate():
        payload = {
            "model": "llama3",
            "messages": [{"role": "user", "content": user_prompt}],
            "stream": True
        }
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))["message"]["content"]
                    yield chunk

    return Response(stream_with_context(generate()), content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
