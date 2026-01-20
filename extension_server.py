from flask import Flask, request, jsonify
from flask_cors import CORS
from pshield import PromptShield

app = Flask(__name__)
CORS(app)

@app.route('/anonymize', methods=['POST'])
def anonymize():
    # Create a new instance for each request to avoid cache conflicts
    anonymizer = PromptShield()
    data = request.json
    text = data.get('text', '')
    result = anonymizer.protect(text)
    mapping = anonymizer.get_mapping()
    return jsonify({'result': result, 'mapping': mapping})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
