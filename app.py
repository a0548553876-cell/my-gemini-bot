import requests
from flask import Flask, request, Response
import re

app = Flask(__name__)

# שים כאן את המפתח שלך
GEMINI_API_KEY = 'AIzaSyA6M5Y3_ajzoUGcbTUI-lkpEv5sTW7ivxs' 

# כאן נשמר הזיכרון של השיחה
chat_history = []

@app.route('/test', methods=['GET', 'POST'])
def test():
    global chat_history
    
    user_input = request.values.get('mytext', '').strip()
    
    # אם המשתמש שותק או שהשיחה התנתקה, אפשר לאפס את הזיכרון (אופציונלי)
    if not user_input:
        return Response("id_list_message=t-לא שמעתי שאלה", mimetype='text/plain')
    
    # אם המשתמש אומר "שלום" או "התחלה", נאפס את הזיכרון
    if user_input in ["שלום", "התחלה", "תפריט"]:
        chat_history = []

    print(f"\n--- שאלה מהטלפון: {user_input} ---")
    
    # הוספת השאלה הנוכחית להיסטוריה
    chat_history.append({"role": "user", "parts": [{"text": user_input}]})

    # הגבלת הזיכרון ל-10 הודעות אחרונות (כדי שלא יהיה ארוך מדי)
    if len(chat_history) > 10:
        chat_history.pop(0)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    # שליחת כל ההיסטוריה לגוגל
    payload = {
        "contents": chat_history,
        "system_instruction": {"parts": [{"text": "ענה בקצרה מאוד בעברית. זכור את תוכן השיחה הקודם."}]}
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if 'candidates' in data and data['candidates']:
            answer = data['candidates'][0]['content']['parts'][0]['text']
            
            # הוספת התשובה של ג'מיני להיסטוריה כדי שהוא יזכור מה הוא ענה
            chat_history.append({"role": "model", "parts": [{"text": answer}]})
            
            clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', answer).strip()
            print(f"תשובה מג'מיני: {clean_text}")
            return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')
        else:
            print(f"שגיאה: {data}")
            return Response("id_list_message=t-סליחה, חלה שגיאה", mimetype='text/plain')
            
    except Exception as e:
        print(f"תקלה: {e}")
        return Response("id_list_message=t-תקלה בשרת", mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)