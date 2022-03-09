from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi
client = MongoClient('mongodb+srv://test:sparta@cluster0.citdv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.dbsparta

@app.route('/main')
def home():
    return render_template('main.html')

# 작성목록을 불러옵니다.
@app.route("/main/list", methods=["GET"])
def item_get():
    item_list = list(db.items.find({}, {'_id': False}))
    reply_list = list(db.reply.find({}, {'_id': False}))
    return jsonify({'items': item_list})

# 댓글을 저장합니다.
@app.route("/main/reply", methods=["post"])
def reply_post():
    reply_receive = request.form['reply_give']
    num_receive = request.form['num_give']

    doc = {
        'num':int(num_receive),
        'reply':reply_receive
    }

    db.reply.insert_one(doc)

    return jsonify({'msg': '댓글을 남겼습니다.!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    # doc = {
    #     'item': item_receive,
    #     'image': image,
    #     'title': title,
    #     'url': url_receive,
    #     'recommend': recommend_receive
    # }
