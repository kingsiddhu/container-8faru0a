from flask import Flask, render_template, request, jsonify
from db import get_db, close_db
import sqlalchemy
from logger import log
import random
from chatbot import *

def getResponse(ints, intents_json,contextToUse):
    try:
        tag = ints[0]['intent']
        print(tag)
        print(contextToUse)
    except:
        return ("Sorry can I cannot understand.",0)
    
    list_of_intents = intents_json['intents']
    if tag == "elaborate":
        for i in list_of_intents:
            print(i["tag"])
            if contextToUse == i["tag"]:
                result = (random.choice(
                    ["Sure! Let me provide more information: ",
                "Certainly! Here's some additional information: ",
                "I'd be happy to elaborate. Here you go: "]
                ) + random.choice(i['responses']), i["context"][0])
                break
        else:
            result = ("I'm not sure how to elaborate on that topic. Please specify a valid topic.",None)
    else:
        for i in list_of_intents:
            """for index in contextToUse:
                if index == tag:
                    result = (random.choice(i['responses']), i["context"][0])
                    break"""
            if(i['tag'] == tag):
                try:
                    result = (random.choice(i['responses']), i["context"][0])
                except:
                    result = (random.choice(i['responses']),None)
                break
    return result


def chatbot_response(msg,context):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents,context)
    return res


app = Flask(__name__)
app.teardown_appcontext(close_db)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    log.info("Checking /health")
    db = get_db()
    health = "BAD"
    try:
        result = db.execute("SELECT NOW()")
        result = result.one()
        health = "OK"
        log.info(f"/health reported OK including database connection: {result}")
    except sqlalchemy.exc.OperationalError as e:
        msg = f"sqlalchemy.exc.OperationalError: {e}"
        log.error(msg)
    except Exception as e:
        msg = f"Error performing healthcheck: {e}"
        log.error(msg)

    return health

@app.route("/get-msg/")
def getuser():
    msg = request.args.get("msg")
    context = request.args.get("context")
    msgCalc = chatbot_response(msg,context)
    if msg and context:
        return jsonify({"msg":msgCalc[0],"context":msgCalc[1]}), 200
    else:
        return "Error 204", 204

