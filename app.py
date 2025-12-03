from flask import Flask, request, render_template
from pshield import PromptShield

pshield = PromptShield()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    original_text = ""
    anonimized_text = "" 
    if request.method == 'POST':
        original_text = request.form.get('user_text', '')
        anonimized_text = pshield.protect(original_text)
    return render_template(
        "prompt_input_form.html",
        original_text=original_text,
        anonimized_text=anonimized_text
    )