from pymongo import MongoClient
import jwt

import datetime

import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

import certifi

client = MongoClient('mongodb+srv://test:sprta@cluster0.aed0m.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = client.dbsparta


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.joinpage.find_one({"userid": payload['userid']})
        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
#로그인 정보가 없는 상태에서는 return 되어 첫화면이 로그인 페이지로 나오게 됨


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')



# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.joinpage.find_one({'userid': id_receive, 'password': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        payload = {
            'userid': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=3600)  # 로그인 1분 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
        # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/name', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.joinpage.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'name': userinfo['name']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# ID 중복확인
@app.route('/api/check_id', methods=['POST'])
def check_id():
    id_receive = request.form['id_give']
    exists = bool(db.joinpage.find_one({"userid": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 회원가입
@app.route('/api/register', methods=['POST'])
def sign_up():

    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    # DB에 저장
    doc = {
        'name': name_receive,
        'userid': id_receive,
        'password': password_hash
    }
    db.joinpage.insert_one(doc)
    return jsonify({'result': 'success'})


# 여기서부터 메인페이지


@app.route('/main')
def main():
    return render_template('index.html')

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/life_item')
def life_item():
    return render_template('life_item.html')

@app.route('/home_elec')
def home_elec():
    return render_template('home_elec.html')

@app.route('/sport_item')
def sport_item():
    return render_template('sport_item.html')

@app.route("/food", methods=["POST"])
def item_post():

    name_receive = request.form['name_give']
    item_receive = request.form['item_give']
    url_receive = request.form['url_give']
    recommend_receive = request.form['recommend_give']



    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']
    title = soup.select_one('meta[property="og:title"]')['content']

    food_list = list(db.items.find({}, {'_id': False}))
    count = len(food_list) + 1
    # print(count)

    doc = {
            'name':name_receive,
            'item':item_receive,
            'image':image,
            'title':title,
            'url':url_receive,
            'recommend':recommend_receive,
            'num':count
    }
    db.items.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})

@app.route("/food/reply", methods=["post"])
def food_reply_post():
    reply_receive = request.form['reply_give']
    num_receive = request.form['num_give']

    doc = {
        'num':int(num_receive),
        'reply':reply_receive
    }

    db.foodreply.insert_one(doc)

    return jsonify({'msg': '댓글을 남겼습니다!'})

@app.route("/foodget", methods=["GET"])
def items_get():
    item_list = list(db.items.find({}, {'_id': False}))
    reply_list = list(db.foodreply.find({}, {'_id': False}))
    return jsonify({'items': item_list, 'replies': reply_list})

@app.route("/life_item", methods=["POST"])
def life_item_post():

    name_receive = request.form['name_give']
    item_receive = request.form['item_give']
    url_receive = request.form['url_give']
    recommend_receive = request.form['recommend_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']
    title = soup.select_one('meta[property="og:title"]')['content']

    life_list = list(db.lifeitem.find({}, {'_id': False}))
    count = len(life_list) + 1
    # print(count)


    doc = {
            'name': name_receive,
            'item': item_receive,
            'image': image,
            'title': title,
            'url': url_receive,
            'recommend': recommend_receive,
            'num':count

    }
    db.lifeitem.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})

@app.route("/life_item/reply", methods=["post"])
def life_reply_post():
    reply_receive = request.form['reply_give']
    num_receive = request.form['num_give']

    doc = {
        'num':int(num_receive),
        'reply':reply_receive
    }

    db.lifeitemreply.insert_one(doc)

    return jsonify({'msg': '댓글을 남겼습니다!'})

@app.route("/life_item_get", methods=["GET"])
def life_items_get():
    life_items_list = list(db.lifeitem.find({}, {'_id': False}))
    reply_list = list(db.lifeitemreply.find({}, {'_id': False}))
    return jsonify({'items': life_items_list, 'replies': reply_list})

@app.route("/home_elec", methods=["POST"])
def home_elec_post():

    item_receive = request.form['item_give']
    url_receive = request.form['url_give']
    recommend_receive = request.form['recommend_give']
    name_receive = request.form['name_give']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']
    title = soup.select_one('meta[property="og:title"]')['content']

    elec_list = list(db.homeelec.find({}, {'_id': False}))
    count = len(elec_list) + 1
    # print(count)
    doc = {
            'name': name_receive,
            'item':item_receive,
            'image':image,
            'title':title,
            'url':url_receive,
            'recommend':recommend_receive,
            'num':count
    }
    db.homeelec.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})

@app.route("/homeelec/reply", methods=["post"])
def elec_reply_post():
    reply_receive = request.form['reply_give']
    num_receive = request.form['num_give']

    doc = {
        'num':int(num_receive),
        'reply':reply_receive
    }

    db.homeelecreply.insert_one(doc)

    return jsonify({'msg': '댓글을 남겼습니다!'})

@app.route("/home_elec_get", methods=["GET"])
def home_elec_get():
    home_elec_list = list(db.homeelec.find({}, {'_id': False}))
    reply_list = list(db.homeelecreply.find({}, {'_id': False}))
    return jsonify({'items': home_elec_list, 'replies': reply_list})

@app.route("/sport_item", methods=["POST"])
def sport_item_post():

    item_receive = request.form['item_give']
    url_receive = request.form['url_give']
    recommend_receive = request.form['recommend_give']
    name_receive = request.form['name_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']
    title = soup.select_one('meta[property="og:title"]')['content']

    elec_list = list(db.sportitem.find({}, {'_id': False}))
    count = len(elec_list) + 1
    # print(count)

    doc = {
            'name': name_receive,
            'item':item_receive,
            'image':image,
            'title':title,
            'url':url_receive,
            'recommend':recommend_receive,
            'num':count
    }
    db.sportitem.insert_one(doc)
    return jsonify({'msg':'등록 완료!'})

@app.route("/sport_item/reply", methods=["post"])
def sport_reply_post():
    reply_receive = request.form['reply_give']
    num_receive = request.form['num_give']

    doc = {
        'num':int(num_receive),
        'reply':reply_receive
    }

    db.sportitemreply.insert_one(doc)

    return jsonify({'msg': '댓글을 남겼습니다!'})

@app.route("/sport_item_get", methods=["GET"])
def sport_item_get():
    sport_item_list = list(db.sportitem.find({}, {'_id': False}))
    reply_list = list(db.sportitemreply.find({}, {'_id': False}))
    return jsonify({'items': sport_item_list, 'replies': reply_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
