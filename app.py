import os
import json
import nltk
from nltk.corpus import wordnet as wn
import requests
from flask import Flask, render_template, send_from_directory
from flask_assets import Environment, Bundle

app = Flask(__name__, static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.urandom(24)
asset = Environment(app)
version = 0.1

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory("js", filename)

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory("css", filename)

@app.route("/res/<path:filename>")
def serve_res(filename):
    return send_from_directory("res", filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api")
def api():
    topics = request.form["topics"]
    date_range = requests.post("https://api.propublica.org/congress/v1/both/votes/2017/02");
    feb_output = json.loads(date_range.text)
    num_results = feb_output["results"]["num_results"]
    votes = {}
    for i in range(num_results):
        vote_object = feb_output["results"]["votes"][i] 
        votes[vote_object["question"]] = vote_object["description"]
        # first determine relevance using wordnet (check if subject matches word or synonym)
        for topic in topics:
            relevant = False
            for synset in wn.synset("topic"):
                for lemma in synset.lemmas:
                    if lemma.name() in vote_object["question"] or lemma.name() in vote_object["description"]:
                        relevant = True
                        break
            if topic in vote_object["question"] or topic in vote_object["description"]:
                relevant = True
        # then determine the overall sentiment (exclude the word in this analysis possibly)
        if relevant:
            # use NLTK semantic analyzer
            return ""

    return ""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True) # turn debug off for production!