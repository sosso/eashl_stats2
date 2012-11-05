from flask import Flask
from flask.globals import request
from main import get_stats
import jsonpickle
import os

app = Flask(__name__)

@app.route('/showstats')
def hello():
    club = str(request.args.get('club')) or ""
    stats = get_stats(club)
    json_stats = jsonpickle.encode(stats)
    return json_stats
    pass

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
