from flask import Flask, request, render_template, jsonify
from pshield import PromptShield
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    original_text = ""
    anonimized_text = ""
    mapping = {}
    
    if request.method == 'POST':
        # Create a new instance for each request to avoid cache conflicts
        pshield = PromptShield()
        original_text = request.form.get('user_text', '')
        anonimized_text = pshield.protect(original_text)
        mapping = pshield.get_mapping()
    
    return render_template(
        "prompt_input_form.html",
        original_text=original_text,
        anonimized_text=anonimized_text,
        mapping=json.dumps(mapping)
    )

@app.route('/restore', methods=['POST'])
def restore():
    """API endpoint to restore a specific placeholder"""
    data = request.get_json()
    text = data.get('text', '')
    placeholder = data.get('placeholder', '')
    mapping = data.get('mapping', {})
    
    if placeholder in mapping:
        restored_text = text.replace(placeholder, mapping[placeholder])
        return jsonify({'success': True, 'text': restored_text})
    
    return jsonify({'success': False, 'text': text})