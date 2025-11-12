from flask import Flask, request, jsonify, render_template
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'), 
            static_folder=os.path.join(base_dir, 'static'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anonymize', methods=['POST'])
def anonymize():
    data = request.json
    text = data.get('text', '')
    
    import re
    anonymized = text
    anonymized = re.sub(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', '[NAME]', anonymized)
    anonymized = re.sub(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '[EMAIL]', anonymized)
    anonymized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', anonymized)
    
    entities_found = len(re.findall(r'\[(NAME|EMAIL|SSN)\]', anonymized))
    
    return jsonify({'anonymized': anonymized, 'entities': entities_found})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
