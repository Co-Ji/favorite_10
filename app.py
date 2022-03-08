from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
import certifi
client = MongoClient('mongodb+srv://test:sparta@cluster0.citdv.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.dbsparta

@app.route('/main')
def home():
    return render_template('main.html')

# @app.route("/api/main", methods=["post"])
# def reply_post():
#     name_receive = request.form['']
#     comment_receive = request.form['comment_give']
#
#
#     doc = {
#         'name':name_receive,
#         'comment':comment_receive
#     }
#
#     db.messages.insert_one(doc)
#
#     return jsonify({'msg': '응원댓글을 남겼습니다!'})

@app.route("/main/list", methods=["GET"])
def item_get():
    item_list = list(db.items.find({}, {'_id': False}))
    return jsonify({'items': item_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    # doc = {
    #     'item': item_receive,
    #     'image': image,
    #     'title': title,
    #     'url': url_receive,
    #     'recommend': recommend_receive
    # }
