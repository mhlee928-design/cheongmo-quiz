import os
from flask import Flask, request, jsonify, send_from_directory
app=Flask(__name__,static_folder="static")

QUESTIONS=[
{"text":"두 사람의 키 차이는?","answers":["15cm","18cm","16cm","17cm"],"correct":1,"detail":"신랑 179cm / 신부 161cm"},
{"text":"두 사람이 사귄 날은? 2월 며칠일까요?","answers":["6일","7일","8일","9일"],"correct":1,"detail":"2월 7일"},
{"text":"두 사람이 둘이서 처음 본 영화는?","answers":["아메바 소녀들과 학교괴담: 개교기념일","수퍼소닉 3","무파사","모아나 2"],"correct":2,"detail":"무파사"},
{"text":"두 사람 카톡에서 더 횟수가 많은 단어는?","answers":["지원(이)","오빠"],"correct":0,"detail":"지원(이) 1871회 / 오빠 1081회 · 횟수는 나중에 수정 가능"},
{"text":"두 사람의 결혼식 날짜는 10월 3일 토요일입니다. 시간은?","answers":["13:30","15:00","16:00","16:30"],"correct":1,"detail":"10월 3일 토요일 15:00 · 기억해주세요!"},
]
AWARDS=[
"신랑신부의 결혼 소식을 듣고 가장 놀랐을 것 같은 사람?",
"결혼식 날 제일 먼저 울 것 같은 사람?",
"결혼식에서 신랑신부보다 사진을 더 많이 찍을 것 같은 사람?",
"결혼식 끝나고 제일 먼저 \"우리 2차 어디야?\" 할 것 같은 사람?",
"신랑신부에게 결혼생활 조언을 제일 많이 할 것 같은 사람?"
]
ROOM={"phase":"lobby","q":-1,"reveal":False,"players":{},"votes":{},"award_q":0}
def pub():
 return {"phase":ROOM["phase"],"q":ROOM["q"],"reveal":ROOM["reveal"],"players":{n:{"score":p["score"],"answered":p["answer"] is not None,"answer":p["answer"],"last_seen":p.get("last_seen",0)} for n,p in ROOM["players"].items()},"votes":ROOM["votes"],"award_q":ROOM["award_q"]}
@app.get("/")
def index(): return send_from_directory("static","index.html")
@app.get("/api/state")
def state(): return jsonify(pub())
@app.get("/api/questions")
def questions(): return jsonify(questions=QUESTIONS,awards=AWARDS)
@app.post("/api/join")
def join():
 n=(request.json or {}).get("name","").strip()
 if not n or len(n)>12:return jsonify(error="이름을 확인해주세요."),400
 ROOM["players"].setdefault(n,{"score":0,"answer":None,"last_seen":0}); return jsonify(ok=True)
@app.post("/api/admin/start")
def start():
 ROOM.update({"phase":"quiz","q":0,"reveal":False,"award_q":0})
 for p in ROOM["players"].values():p["answer"]=None
 return jsonify(ok=True)
@app.post("/api/heartbeat")
def heartbeat():
    import time
    n=(request.json or {}).get("name")
    if n in ROOM["players"]: ROOM["players"][n]["last_seen"]=time.time()
    return jsonify(ok=True)

@app.post("/api/answer")
def answer():
 d=request.json or {};n=d.get("name");a=d.get("answer")
 if n not in ROOM["players"] or ROOM["phase"]!="quiz" or ROOM["reveal"]:return jsonify(error="현재 답변할 수 없습니다."),400
 ROOM["players"][n]["answer"]=a
 import time
 ROOM["players"][n]["last_seen"]=time.time()
 return jsonify(ok=True)
@app.post("/api/admin/reveal")
def reveal():
 c=QUESTIONS[ROOM["q"]]["correct"]
 for p in ROOM["players"].values():
  if p["answer"]==c:p["score"]+=1
 ROOM["reveal"]=True;return jsonify(ok=True,correct=c)
@app.post("/api/admin/next")
def nextq():
 if ROOM["q"]>=len(QUESTIONS)-1:ROOM["phase"]="awards";ROOM["award_q"]=0
 else:ROOM["q"]+=1
 ROOM["reveal"]=False
 for p in ROOM["players"].values():p["answer"]=None
 return jsonify(ok=True)
@app.post("/api/award")
def award():
 d=request.json or {};v=d.get("voter");s=d.get("selected")
 if ROOM["phase"]!="awards" or v not in ROOM["players"]:return jsonify(error="투표 오류"),400
 ROOM["votes"][f"{ROOM['award_q']}|{v}"]=s;return jsonify(ok=True)
@app.post("/api/admin/award-next")
def award_next():
 if ROOM["award_q"]>=len(AWARDS)-1:ROOM["phase"]="final"
 else:ROOM["award_q"]+=1
 return jsonify(ok=True)
@app.get("/api/admin/award-results")
def results():
 out=[]
 for q in range(len(AWARDS)):
  c={}
  for k,v in ROOM["votes"].items():
   if k.startswith(str(q)+"|"):c[v]=c.get(v,0)+1
  out.append(c)
 return jsonify(results=out)
@app.post("/api/admin/reset")
def reset():
 ROOM.update({"phase":"lobby","q":-1,"reveal":False,"players":{},"votes":{},"award_q":0});return jsonify(ok=True)
if __name__=="__main__":app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
