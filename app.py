from flask import Flask, render_template, request
#from flask_mysqldb import MySQL
from flask_cors import CORS
from googleapiclient import discovery
from textblob import TextBlob
import json, os
from sklearn.externals import joblib
from nltk.tokenize import sent_tokenize

from flask_sqlalchemy import SQLAlchemy

from models import Users, Edits, db

# clf_wassem = joblib.load('svc-wassem.pkl')
# tf_idf_wassem = joblib.load('tfidf-wassem.pkl')
# clf_dav = joblib.load('svc-davidson.pkl')
# tf_idf_dav = joblib.load('tfidf-davidson.pkl')
# wassem = ["Racism", "Sexism", "None"]
tfidf = joblib.load('tfidf-embeddings.pkl')
svcWordType = joblib.load('svc-word-type.pkl')
svcWordEntity = joblib.load('svc-word-entity.pkl')
svcCharType = joblib.load('svc-character-type.pkl')
svcCharEntity = joblib.load('svc-character-entity.pkl')
typeLabel = ["None", "Hate Speech", "Offensive", "Harassment"]
entityLabel = ["", "Racism", "Sexism", "Offensive", "Abusive", "Harassment"]

app = Flask(__name__)

#app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/prosocial'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xghjfozhdmbkdo:78c4a3adb92ea8f1b8d135888040a87320903e6c83ea786007839cef97ffd164@ec2-54-247-82-210.eu-west-1.compute.amazonaws.com:5432/d8h6ie6g74jmgo'
db.init_app(app)


# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'backend-extension'
app.config['MYSQL_HOST'] = 'localhost'
#mysql = MySQL(app)
#conn = mysql.connect()
#cursor = conn.cursor()
CORS(app)

@app.route('/')
def hello_world():
    # cur = mysql.connection.cursor()
    # cur.execute('INSERT INTO users(name, handler) VALUES(%s, %s)', ("myname", "handler"))
    # mysql.connection.commit()
    # # Close connection
    # cur.close()
    userId = 0
    result = userExists("handler")
    user = result[0];
    if user:
        userId = result[1][0]
    return "Hello World from backend " + "user Id " + str(userId)

@app.route('/registerUser', methods=['POST'])
def registerUser():
    data = request.form
    userName = data['userName']
    handler = data['handler']
    result = userExists(handler)
    user = result[0];
    if user:
        resp = {"status": "User already exists"}
        return json.dumps(resp)
    else:
        # cur = mysql.connection.cursor()
        # cur.execute('INSERT INTO users(name, handler) VALUES(%s, %s)', (userName, handler))
        # mysql.connection.commit()
        # cur.close()
        resp = {"status": "User created successfully"}
        return json.dumps(resp)

@app.route('/tweet-complete', methods=['POST'])
def tweetComplete():
    data = request.form
    print(data.keys())
    handler = data['handler']
    finalTweet = data['finalTweet'],
    edits = data['edits'],
    noOfEdits = data['noOfEdits'],
    messageShown = data['messageShown']
    print("Data recieved ", finalTweet, " by user ", handler)
    #result = userExists(userName)
    #user = result[0];
    #userId = result[1][0]
    resp = saveEdits(handler, finalTweet, edits, noOfEdits, messageShown)
    return json.dumps(resp)

@app.route('/tweet-analysis-live', methods=["GET",'POST'])
def postRequest():
    data = request.form
    #userName = data['userName']
    text = data['text']
    response = handleIncomingTweet(text)
    return json.dumps(response)

@app.route('/comment-detect', methods=['POST'])
def commentDetect():
    data = request.form
    text = data['text']
    response = handleIncomingTweet(text)
    resp = {
        "toxicity": response["toxicity"],
        "label": response["labelEnt"],
        "sentiment": response["sentiment"]
    }
    return json.dumps(resp)

@app.route('/getAllTweets', methods=['GET'])
def getAllTweets():
    data = request.form
    text = data['text']
    response = handleIncomingTweet(text)
    resp = {
        "toxicity": response["toxicity"],
        "label": response["labelEnt"],
        "sentiment": response["sentiment"]
    }
    return json.dumps(resp)



@app.route('/saveUser', methods=['POST'])
def saveUser():
    data = request.form
    handler = data['handler']
    print(handler);
    try:
        user = Users(
            name = '',
            handler = handler
        )
        db.session.add(user)
        db.session.commit()
        print("User Id", user.id)
        return "User added. User id={}".format(user.id)
    except Exception as e:
        print(str(e))
        return (str(e))
    resp = {"status": "Success"}
    return json.dumps(resp)

def handleIncomingTweet(text):
    toxicity = perspective(text)
    #toxicity = 0.5
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    vct = tfidf.transform([text])
    wordType = svcWordType.predict(vct)
    wordEntity = svcWordEntity.predict(vct)
    charType = svcCharType.predict(vct)
    charEntity = svcCharEntity.predict(vct)
    labelT = typeLabel[charType[0]]
    labelEnt = entityLabel[charEntity[0]]
    resp = {'toxic': False, 'notify': True, "labelT":labelT, "labelEnt":labelEnt, 'toxicity': toxicity ,'sentiment':sentiment, 'nagative': False, 'message':'', 'title': "Title"}
    resp['toxic'] = toxicity >= 0.3
    resp['negative'] = sentiment <= -0.4

    if labelEnt == "Sexism":
        resp['title'] = labelEnt
        resp['message'] = "People don't like it often when addressed like this. This message could be conveyed in some other way."
    elif labelEnt == "Abusive":
        resp['title'] = labelEnt
        resp['message'] = "No one likes to be hatred. Your audience may find it be hate speech and they can report you on this."
    elif labelEnt == "Offensive":
        resp['title'] = labelEnt
        resp['message'] = "Google Comment Api marked this tweet as toxic. Your audience will find it negatively addressed. You can try another way to convey your message."
    elif labelEnt =="Racism":
        resp['title'] = "Toxic tweet"
        resp['message'] = "Google Comments Api marked this tweet as toxic. It may not please your audience."
    elif labelEnt =="Harassment":
        resp['title'] = labelEnt
        resp[
            'message'] = "Most of the people will find this tweet as negative. You can try another way to convey your message."
    else:
        resp['title'] = labelEnt
        resp['message'] = "Majority will find this tweet as offensive. You can alwyas try another way to convey your message."


    if resp['message'] != '':
        resp['notify'] = True
    else:
        if toxicity >= 0.4:
            resp['message'] = "Majority will find this tweet as offensive. You can alwyas try another way to convey your message."
            resp['notify'] = True
    if resp['notify'] == True:
        if sentiment >= -0.2:
            resp['notify'] = False

    print("After textBlob", resp)
    #res = "Google Perspective Api's Toxicity Probability " + str(toxicity) + " and Sentiment Polarity score " + str(sentiment)
    #print("Response ", res)
    return resp

def saveEdits(handler, finalTweet, edits, noOfEdits, messageShown):
    try:
        edit = Edits(
            handler=handler,
            finalTweet = finalTweet,
            edits = edits,
            noOfEdits = noOfEdits,
            messageShown = messageShown
        )
        db.session.add(edit)
        db.session.commit()
        return "Edits added. Edit id={}".format(edit.id)

    except Exception as e:
        return (str(e))
    resp = {"status": "Success"}
    return resp


def userExists(_handler):
    try:
        book = Users.query.filter_by(handler=_handler).first()
        print(book.serialize())
        return [True, 1]
    except Exception as e:
        return [False, None]


def perspective(text):
    API_KEY = 'AIzaSyB4UCmP4e3ne2t2zYqDM6R7o69Fih03mVU'
    # Generates API client object dynamically based on service name and version.
    service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

    analyze_request = {
        'comment': {'text': text},
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = service.comments().analyze(body=analyze_request).execute()
    res = json.dumps(response)
    # print(json.dumps(response))
    toxicity = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

    return toxicity
