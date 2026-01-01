import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# הגדרת מפתח ה-API
GEMINI_API_KEY = 'AIzaSyA6M5Y3_ajzoUGcbTUI- lkpEv5sTW7ivxs'
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# זיכרון שיחה
chat_session = model.start_chat(history=[])

@app.route('/test', methods=['GET', 'POST'])
def test():
    # ימות המשיח שולחים את הלינק להקלטה בפרמטר שנקרא 'val' (או שם אחר שתבחר)
    file_url = request.values.get('file_url', '').strip()
    
    if not file_url:
        return Response("id_list_message=t-לא התקבלה הקלטה", mimetype='text/plain')

    try:
        print(f"מוריד קובץ אודיו: {file_url}")
        # הורדת הקובץ זמנית לשרת
        audio_data = requests.get(file_url).content
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data)

        # שליחה לג'מיני (הוא מבצע גם את הזיהוי וגם את התשובה)
        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        
        response = chat_session.send_message([
            sample_file,
            "הקשב להקלטה וענה עליה בקצרה מאוד בעברית."
        ])
        
        answer = response.text
        # ניקוי תווים מיוחדים
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', answer).strip()
        
        print(f"ג'מיני ענה: {clean_text}")
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"שגיאה: {e}")
        return Response("id_list_message=t-תקלה בעיבוד האודיו", mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
