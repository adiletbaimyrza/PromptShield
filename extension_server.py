from flask import Flask, request, jsonify
from flask_cors import CORS
from pshield import PromptShield

app = Flask(__name__)
CORS(app)

anonymizer = PromptShield()

@app.route('/anonymize', methods=['POST'])
def anonymize():
    data = request.json
    text = data.get('text', '')
    result = anonymizer.protect(text)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
