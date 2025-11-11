from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    anonimized_text = None
    if request.method == 'POST':
        anonimized_text = request.form.get('user_text') # Placeholder for actual anonimization logic
    return render_template("prompt_input_form.html", anonimized_text=anonimized_text)
