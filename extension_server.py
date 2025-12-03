from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.append('services')
from anonimize import anonimizacja

app = Flask(__name__)
CORS(app)

@app.route('/anonymize', methods=['POST'])
def anonymize():
    data = request.json
    text = data.get('text', '')
    result = anonimizacja(text)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
