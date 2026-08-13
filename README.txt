같이놀자 청모 실시간 웹앱

주요 기능
- 신랑신부 QUIZ: 동시 진행, 정답 공개, 점수 집계
- 같이놀자 AWARDS: 동시 투표 → 결과 공개 → 다음 어워즈
- 진행자 화면: 참가자 온라인/응답/투표 현황 및 참가자 화면 미리보기
- 관리자 화면에서 게임 시작 전 문제, 보기, 정답, 해설, AWARDS 질문 직접 수정
- 현재 서버 세션 동안 수정 내용 유지

Render 설정
Build Command: pip install -r requirements.txt
Start Command: gunicorn server:app

추가 수정: 새로 링크를 열면 항상 첫 화면에서 시작하도록 참가자 이름을 localStorage에 저장하지 않게 했습니다. 대기 화면에도 '처음 화면으로' 버튼을 추가했습니다.
