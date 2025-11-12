from flask import Flask, request, render_template
from services.anonimizacja import anonimizacja

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    original_text = ""
    anonimized_text = "" 
    if request.method == 'POST':
        original_text = request.form.get('user_text', '')
        anonimized_text = anonimizacja(original_text)
    return render_template(
        "prompt_input_form.html",
        original_text=original_text,
        anonimized_text=anonimized_text
    )