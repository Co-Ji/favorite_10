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
    return jsonify({'items': item_list, 'replys': reply_list})

# 댓글을 저장합니다.
@app.route("/main/reply", methods=["post"])
def reply_post():
    reply_receive = request.form['reply_give']
    num_receive = request.form['num_give']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/life_item')
def life_item():
    return render_template('life_item.html')

@app.route('/home_elec')
def home_elec():
    return render_template('home_elec.html')

@app.route('/sport_item')
def sport_item():
    return render_template('sport_item.html')


@app.route("/item", methods=["POST"])
def item_post():
    count = len(num) + 1
    item_receive = request.form['item_give']
    url_receive = request.form['url_give']
    recommend_receive = request.form['recommend_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']
    title = soup.select_one('meta[property="og:title"]')['content']


    doc = {
            'num': count,
            'item':item_receive,
            'image':image,
            'title':title,
            'url':url_receive,
            'recommend':recommend_receive
    }
    db.items.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})



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
