import os
import json
import ast
import nltk
from nltk.corpus import wordnet as wn
import requests
from flask import Flask, render_template, send_from_directory, Response, request, jsonify
from flask_assets import Environment, Bundle
import logging

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

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        topics = json.loads(request.form["topics"])
        date_range = requests.get("https://api.propublica.org/congress/v1/both/votes/2017/03.json", headers={"X-API-Key":"fFpjOt2GQJjCZV70ynIMuNE0yrBHlrNSQYhWZcal"})
        mar_output = json.loads(date_range.text)
        num_results = mar_output["results"]["num_results"]
        results = []
        relevant = False
        for i in range(num_results-(num_results/10)):
            vote_object = mar_output["results"]["votes"][i]
            # first determine relevance using wordnet (check if subject matches word or synonym)
            for topic in topics.iterkeys():
                relevant = False
                for synset in wn.synsets(topic):
                    for l in synset.lemmas():
                        if l.name() in vote_object["question"] or l.name() in vote_object["description"]:
                            relevant = True
                if topic in vote_object["question"] or topic in vote_object["description"]:
                    relevant = True
            # then determine the overall sentiment (exclude the word in this analysis possibly)
            if relevant:
                # use NLTK sentiment analysis
                shippy = requests.get("http://text-processing.com/api/sentiment", data={"text":vote_object["question"]+""+vote_object["description"]})
                try:
                    sent_label = json.loads(shippy.text)["label"]
                except:
                    # welp no data
                    continue
                results.append(vote_object["question"], vote_object["description"], sent_label)
        results = json.dumps(results)
        app.logger.info("Dumped JSON\n"+results)
        lan = requests.get("http://whoismyrepresentative.com/getall_mems.php?zip="+request.form["zip"]+"&output=json")
        lan = json.loads(lan.text)
        

        return jsonify(results)
    else:
        return "method not allowed"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True) # turn debug off for production!