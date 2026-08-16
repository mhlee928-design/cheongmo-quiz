import os, time
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

QUESTIONS = [
  {"text":"지현의 말투가 아닌 것은?","answers":["나빴네!","니 뜨겁나!","우리 형이 짱이지!","맞지맞지 사실인걸?"],"correct":1,"detail":"'니 뜨겁나!'는 한 적이 없습니다..."},
    
    {"text":"지원의 MBTI는?","answers":["ESFJ","ISTJ","ISFJ","ESTJ"],"correct":0,"detail":"나 T 아니야"},
    
    {"text":"지현,지원의 키 차이는?","answers":["16cm","17cm","18cm","19cm"],"correct":2,"detail":"지현 179cm / 지원 161cm"},
    
    {"text":"두 사람의 사귄 날은 몇월일까요?","answers":["24년 12월","25년 1월","25년 2월","25년 3월"],"correct":2,"detail":""},
    
    {"text":"두 사람이 둘이서 처음 본 영화는?","answers":["소녀들과 학교괴담: 개교기념일","수퍼소닉 3","모아나 2","무파사: 라이온 킹"],"correct":3,"detail":""},
    
    {"text":"두 사람의 카톡방에서 말한 횟수가 더 많은 단어는?","answers":["지원이","오빠"],"correct":0,"detail":"지원이 1871회 / 오빠 1218회 (2026.08.13. 기준)"},
    
    {"text":"지현이가 지원이에게 가장 많이 듣는 말은?","answers":["오늘 뭐 먹을래","그럴 수 있지","집에 안가니","나 챗지피티 아니야"],"correct":3,"detail":""},
    
    {"text":"만약 지현,지원의 2세가 생긴다면 나올 수 없는 혈액형은?","answers":["O","A","B","AB"],"correct":0,"detail":"지현 AB / 지원 A"},
    
    {"text":"지지커플의 결혼식 날짜는 10월 3일 토요일입니다. 시간은?","answers":["14:30","15:00","16:00","16:30"],"correct":1,"detail":"10월 3일 토요일 15:00 · 기억해주세요!"},
    
{
    "text":"신랑신부에게 가장 어울리는 한마디?",
    "answers":[
        "평생 행복하게 살아라",
        "싸우지 말고 잘 살아라",
        "둘이 알아서 잘하겠지",
        "결혼해도 같이놀자"
    ],
    "correct":-1,
    "detail":"①~④ 모두 정답! 여러분의 마음이 모두 정답입니다 💕"
},
]

AWARDS = [
    "결혼식에서 가장 먼저 신랑신부를 놀릴 것 같은 사람?",
    "결혼식 날 제일 먼저 도착할 것 같은 사람?",
    "결혼식 끝나고 제일 먼저 \"우리 2차 어디야?\" 할 것 같은 사람?",
    "식장에 포토부스(웨딩네컷사진기)가 있는데, 포토부스 사진첩에 가장 많이 등장할 것 같은 사람?",
    "신랑신부에게 결혼생활 조언을 제일 많이 할 것 같은 사람?",
]

ROOM = {"phase":"lobby","q":-1,"reveal":False,"award_reveal":False,
        "players":{},"votes":{},"award_q":0}

def public_state():
    return {
        "phase":ROOM["phase"], "q":ROOM["q"], "reveal":ROOM["reveal"],
        "award_reveal":ROOM["award_reveal"], "award_q":ROOM["award_q"],
        "players":{
            n:{"score":p["score"],"answered":p["answer"] is not None,
               "answer":p["answer"],"last_seen":p.get("last_seen",0)}
            for n,p in ROOM["players"].items()
        },
        "votes":ROOM["votes"]
    }

@app.get("/")
def index():
    return send_from_directory("static","index.html")

@app.get("/api/state")
def state():
    return jsonify(public_state())

@app.get("/api/questions")
def questions():
    return jsonify(questions=QUESTIONS, awards=AWARDS)

@app.post("/api/join")
def join():
    n=str((request.json or {}).get("name","")).strip()
    if not n or len(n)>12:
        return jsonify(error="이름을 확인해주세요."),400
    ROOM["players"].setdefault(n,{"score":0,"answer":None,"last_seen":time.time()})
    ROOM["players"][n]["last_seen"]=time.time()
    return jsonify(ok=True)

@app.post("/api/admin/start")
def start():
    if not QUESTIONS:
        return jsonify(error="문제가 없습니다."),400
    ROOM.update({"phase":"quiz","q":0,"reveal":False,"award_reveal":False,"award_q":0,"votes":{}})
    for p in ROOM["players"].values():
        p["answer"]=None
        p["score"]=0
    return jsonify(ok=True)

@app.post("/api/heartbeat")
def heartbeat():
    n=(request.json or {}).get("name")
    if n in ROOM["players"]:
        ROOM["players"][n]["last_seen"]=time.time()
    return jsonify(ok=True)

@app.post("/api/answer")
def answer():
    d=request.json or {}; n=d.get("name"); a=d.get("answer")
    if n not in ROOM["players"] or ROOM["phase"]!="quiz" or ROOM["reveal"]:
        return jsonify(error="현재 답변할 수 없습니다."),400
    if not isinstance(a,int) or not 0 <= a < len(QUESTIONS[ROOM["q"]]["answers"]):
        return jsonify(error="답변을 확인해주세요."),400
    ROOM["players"][n]["answer"]=a
    ROOM["players"][n]["last_seen"]=time.time()
    return jsonify(ok=True)

@app.post("/api/admin/reveal")
def reveal():
    if ROOM["phase"]!="quiz" or ROOM["reveal"]:
        return jsonify(error="정답을 공개할 수 없습니다."),400

    c=QUESTIONS[ROOM["q"]]["correct"]

    for p in ROOM["players"].values():
        if c == -1 or p["answer"] == c:
            p["score"] += 1

    ROOM["reveal"]=True
    return jsonify(ok=True,correct=c)

@app.post("/api/admin/next")
def nextq():
    if ROOM["phase"]!="quiz" or not ROOM["reveal"]:
        return jsonify(error="먼저 정답을 공개해주세요."),400
    if ROOM["q"] >= len(QUESTIONS)-1:
        ROOM["phase"]="quiz_final"
        ROOM["reveal"]=False
    else:
        ROOM["q"]+=1; ROOM["reveal"]=False
    for p in ROOM["players"].values():
        p["answer"]=None
    return jsonify(ok=True)

@app.post("/api/admin/start-awards")
def start_awards():
    if ROOM["phase"] != "quiz_final":
        return jsonify(error="QUIZ 최종 결과 화면에서만 AWARDS를 시작할 수 있습니다."),400
    ROOM["phase"]="awards"
    ROOM["award_q"]=0
    ROOM["award_reveal"]=False
    return jsonify(ok=True)

@app.post("/api/award")
def award():
    d=request.json or {}; v=d.get("voter"); selected=d.get("selected")
    if ROOM["phase"]!="awards" or ROOM["award_reveal"] or v not in ROOM["players"]:
        return jsonify(error="현재 투표할 수 없습니다."),400
    if selected not in ROOM["players"]:
        return jsonify(error="참가자를 선택해주세요."),400
    ROOM["votes"][f"{ROOM['award_q']}|{v}"]=selected
    ROOM["players"][v]["last_seen"]=time.time()
    return jsonify(ok=True)

@app.post("/api/admin/award-reveal")
def award_reveal():
    if ROOM["phase"]!="awards" or ROOM["award_reveal"]:
        return jsonify(error="현재 결과를 공개할 수 없습니다."),400
    ROOM["award_reveal"]=True
    return jsonify(ok=True)

@app.post("/api/admin/award-next")
def award_next():
    if ROOM["phase"]!="awards" or not ROOM["award_reveal"]:
        return jsonify(error="먼저 AWARDS 결과를 공개해주세요."),400
    if ROOM["award_q"] >= len(AWARDS)-1:
        ROOM["phase"]="final"
    else:
        ROOM["award_q"]+=1
        ROOM["award_reveal"]=False
    return jsonify(ok=True)

@app.post("/api/admin/final")
def final_result():
    if ROOM["phase"] not in ("awards", "final"):
        return jsonify(error="최종 결과를 공개할 수 없습니다."),400

    ROOM["phase"] = "final"
    return jsonify(ok=True)

@app.get("/api/admin/award-results")
def results():
    out=[]
    for q in range(len(AWARDS)):
        c={}
        for k,v in ROOM["votes"].items():
            if k.startswith(str(q)+"|"):
                c[v]=c.get(v,0)+1
        out.append(c)
    return jsonify(results=out)

@app.post("/api/admin/reset")
def reset():
    ROOM.update({"phase":"lobby","q":-1,"reveal":False,"award_reveal":False,
                 "players":{},"votes":{},"award_q":0})
    return jsonify(ok=True)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
