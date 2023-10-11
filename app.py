from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import re

app = Flask(__name__)

client = MongoClient("mongodb://test:test@54.180.100.137", 27017)
db = client.square

# db에 넣을 가데이터 나중에 제거해줘야함
list_user = [
    {
        "userid": "123",
        "username": "john_doe",
        "password": "123",
        "max_score": 98.77,
        "max_score_date": "23/10/13",
    },
    {
        "userid": "456",
        "username": "jane_smith",
        "password": "123",
        "max_score": 95.44,
        "max_score_date": "23/10/12",
    },
    {
        "userid": "789",
        "username": "alice_wonderland",
        "password": "123",
        "max_score": 90.22,
        "max_score_date": "23/10/10",
    },
    {
        "userid": "101112",
        "username": "ghibli",
        "password": "pass123",
        "max_score": 0,
        "max_score_date": "23/10/10",
    },
]
# 현재 db를 비우고 가데이터를 넣는다
db.users.delete_many({})
db.users.insert_many(list_user)


# API # : main(가짜)
@app.route("/main")
def main():
    return render_template("main.j2", message="hello")


# API # : 랭킹 보여주기
@app.route("/ranking")
def show_rankings():
    # db에서 max_score가 0인 유저(=플레이 하지 않음)를 제외한 전체 데이터를 가져온다
    list_user = list(db.users.find({"max_score": {"$ne": 0}}))

    # db의 유저를 max_score 내림차순으로 정렬한다
    list_user.sort(key=lambda field: field["max_score"], reverse=True)

    # 순위를 계산하여 각 유저 데이터에 추가
    rank = 1
    for user in list_user:
        user['rank'] = rank
        rank += 1

    # 정렬된 유저 데이터를 적절히 가공해서 출력한다
    return render_template("ranking.j2", list_user=list_user)


# API # : 회원 가입 페이지 보여주기
@app.route("/signup")
def show_signup():
    # 회원가입 페이지 렌더링
    return render_template("signup.j2")


# API # : 회원 가입 처리
@app.route("/signup_process", methods=["POST"])
def signup_process():
    if request.method == "POST":
        # 사용자가 제출한 데이터 가져오기
        data = request.json

        userid = data["userid"]
        password = data["password"]
        password_confirm = data["password_confirm"]
        username = data["username"]

        # 에러를 받을 딕셔너리를 만든다
        errors = {}
        
        # 유저 id가 영문, 숫자가 아니면 에러 메세지를 반환한다
        pattern = "^[A-Za-z0-9]+$"
        if not re.match(pattern, userid):
            errors["useridError"] = "id는 영문 및 숫자로 구성되어야 합니다"
        
        # 유저 id가 너무 짧으면 에러 메세지를 반환한다
        if len(userid) <= 3:
            errors["useridError"] = "id가 너무 짧습니다"

        # 유저 id에 공백이 있으면 에러 메세지를 반환한다
        if ' ' in userid:
            errors["useridError"] = "id에는 공백이 없어야 합니다"
        
        # 유저 이름이 너무 짧으면 에러 메세지를 반환한다
        if len(username) <= 1:
            errors["usernameError"] = "이름이 너무 짧습니다"

        # 유저 이름에 공백이 있으면 에러 메세지를 반환한다
        if ' ' in username:
            errors["usernameError"] = "이름에는 공백이 없어야 합니다"
        
        # 패스워드가 너무 짧으면 에러 메세지를 반환한다
        if len(password) <= 4:
            errors["passwordconfirmError"] = "패스워드가 너무 짧습니다"

        # 패스워드가 일치하지 않으면 에러 메세지를 반환한다
        if password != password_confirm:
            errors["passwordconfirmError"] = "패스워드가 일치하지 않습니다"

        # 유저 id가 기존에 있는지 검증한다. 있으면 에러 메세지를 띄운다
        check_userid = db.users.find_one({"userid": userid})
        check_username = db.users.find_one({"username": username})
        if check_userid is not None:
            errors["useridError"] = "이미 등록된 아이디입니다"
        if check_username is not None:
            errors["usernameError"] = "이미 등록된 이름입니다"

        # 에러가 있으면 클라이언트에 반환한다
        if errors:
            return jsonify(errors)

        # 검증을 통과하면 db에 유저 정보를 저장한다.
        user_new = {
            "userid": userid,
            "username": username,
            "password": password,
            "max_score": 0,
            "max_score_date": "",
        }
        db.users.insert_one(user_new)
        # # 성공하면 메인 페이지로 돌아간다
        return jsonify({"success":"회원 가입이 완료되었습니다!"})
        return redirect("/main")

app.run("0.0.0.0", port=5020, threaded=True, debug=True)
