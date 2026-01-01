import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# הגדרת מפתח ה-API של ג'מיני
GEMINI_API_KEY = 'AIzaSyA6M5Y3_ajzoUGcbTUI- lkpEv5sTW7ivxs'
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/test', methods=['GET', 'POST'])
def test():
    # קבלת הלינק לקובץ האודיו מימות המשיח
    file_url = request.values.get('file_url', '').strip()
    
    # אם השרת לא קיבל לינק, הוא לא יקרוס אלא יחזיר הודעה מסודרת
    if not file_url or file_url == '%path%':
        print("Error: No valid file_url received")
        return Response("id_list_message=t-לא התקבלה הקלטה תקינה", mimetype='text/plain')

    try:
        print(f"Processing audio from: {file_url}")
        
        # הורדת הקובץ זמנית לשרת ה-Render
        response_audio = requests.get(file_url, timeout=10)
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # שליחה לג'מיני לתימלול ומענה
        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        
        # בקשה מג'מיני (הוא עושה הכל - גם שומע וגם עונה)
        response = model.generate_content([
            sample_file,
            "הקשב להקלטה וענה עליה בקצרה מאוד בעברית (עד 20 מילים)."
        ])
        
        answer = response.text
        # ניקוי הטקסט כדי שימות המשיח יוכלו להקריא אותו (בלי כוכביות וסימנים מוזרים)
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', answer).strip()
        
        print(f"Gemini response: {clean_text}")
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"Detailed Error: {str(e)}")
        # מחזיר את השגיאה כטקסט לטלפון כדי שנדע מה קרה
        return Response(f"id_list_message=t-שגיאה בעיבוד. {str(e)[:20]}", mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
