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
    # הדפסת כל הפרמטרים ללוגים לצורך ניפוי שגיאות
    print(f"DEBUG: All received params: {request.values.to_dict()}")
    
    # ניסיון לקבל את הלינק מכל שם אפשרי שימות המשיח שולחים
    file_url = request.values.get('file_url') or request.values.get('val')
    
    # בדיקה אם הלינק תקין ולא מכיל את המשתנה הגולמי %path%
    if not file_url or "%" in str(file_url):
        print(f"Error: Invalid file_url received: {file_url}")
        return Response("id_list_message=t-נא להקליט שוב לאחר הצליל", mimetype='text/plain')

    try:
        print(f"Processing audio from: {file_url}")
        
        # הורדת קובץ האודיו
        response_audio = requests.get(file_url, timeout=15)
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # העלאה לג'מיני וקבלת תשובה
        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        response = model.generate_content([
            sample_file,
            "הקשב להקלטה וענה עליה בקצרה מאוד בעברית (עד 20 מילים)."
        ])
        
        answer = response.text
        # ניקוי תווים מיוחדים שלא נתמכים בימות המשיח
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', answer).strip()
        
        print(f"Gemini response: {clean_text}")
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"Detailed Error: {str(e)}")
        return Response(f"id_list_message=t-שגיאה בעיבוד {str(e)[:15]}", mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
