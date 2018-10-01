from flask import Flask, render_template, request
#from flask_cors import CORS
from googleapiclient import discovery
from textblob import TextBlob
import json
from sklearn.externals import joblib
from nltk.tokenize import sent_tokenize

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

# MySQL configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'backend-extension'
app.config['MYSQL_HOST'] = 'localhost'
#mysql = MySQL(app)
#conn = mysql.connect()
#cursor = conn.cursor()
#CORS(app)

@app.route('/')
def hello_world():
    # cur = mysql.connection.cursor()
    # cur.execute('INSERT INTO users(name, handler) VALUES(%s, %s)', ("myname", "handler"))
    # mysql.connection.commit()
    # # Close connection
    # cur.close()
    # userId = 0
    # result = userExists("handler")
    # user = result[0];
    # if user:
    #     userId = result[1][0]
    return "Hello World"

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
    #data = dat['data']
    print(data.keys())
    userName = data['userName']
    text = data['text']
    print("Data recieved ", text, " by user ", userName)
    result = userExists(userName)
    user = result[0];
    if user:
        userId = result[1][0]
        resp = saveTweet(userId, text)
        return json.dumps(resp)
    else:
        resp = {"status": "Couldn't find the user"}
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



@app.route('/gmail-live', methods=['POST'])
def emailDetect():
    data = request.form
    text = data['text']
    sent_list = sent_tokenize(text)
    print("Size of list ", sent_list)
    response = handleIncomingTweet(text)
    resp = []
    for sent in sent_list:
        response = handleIncomingTweet(text)
        if response['notify'] == True:
            r = {
                "sentence": sent,
                "response": response
            }
        resp.append(r)
    return json.dumps(resp)


def handleIncomingTweet(text):
    #toxicity = perspective(text)
    toxicity = 0.5
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
    resp['toxic'] = toxicity >= 0.4
    resp['negative'] = sentiment <= -0.4

    if labelEnt == "Sexism":
        resp['title'] = labelEnt
        resp['message'] = "People don't like it often when addressed like this. This message could be conveyed in some other way."
    elif labelEnt != "Abusive":
        resp['title'] = labelEnt
        resp['message'] = "No one likes to be hatred. Your audience may find it be hate speech and they can report you on this."
    elif labelEnt == "Offensive":
        resp['title'] = labelEnt
        resp['message'] = "Google Comment Api marked this tweet as toxic. Your audience will find it negatively addressed. You can try another way to convey your message."
    elif labelEnt=="Racism":
        resp['title'] = "Toxic tweet"
        resp['message'] = "Google Comments Api marked this tweet as toxic. It may not please your audience."
    elif labelEnt=="Harassment":
        resp['title'] = labelEnt
        resp[
            'message'] = "Most of the people will find this tweet as negative. You can try another way to convey your message."
    else:
        resp['title'] = labelEnt
        resp['message'] = "Majority will find this tweet as offensive. You can alwyas try another way to convey your message."


    if resp['message'] != '':
        resp['notify'] = True

    print("After textBlob")
    #res = "Google Perspective Api's Toxicity Probability " + str(toxicity) + " and Sentiment Polarity score " + str(sentiment)
    #print("Response ", res)
    return resp

def saveTweet(id, tweet):
    # cur = mysql.connection.cursor()
    # cur.execute('INSERT INTO tweets(userId, text) VALUES(%s, %s)', (id, tweet))
    # mysql.connection.commit()
    # cur.close()
    resp = {"status": "Success"}
    return resp

def userExists(handler):
    return [True, 1]
    # cur = mysql.connection.cursor()
    # q = 'SELECT id, name, handler from users where handler=' + handler
    # cur.execute(q)
    # data = cur.fetchone()
    # cur.close()
    # if data is None:
    #     return [False, None]
    # else:
    #     d = list(data)
    #     return [True, d]


def getUserID(handler):
    print("Get the user id given the handler")

def perspective(text):
    API_KEY = 'AIzaSyAiBsN6uIt8Nti_8emcbFS9TN5dAqne1zY'
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

