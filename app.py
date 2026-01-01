import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# הגדרת מפתח ה-API של ג'מיני - וודא שהמפתח שלך כאן!
GEMINI_API_KEY = 'AIzaSyA6M5Y3_ajzoUGcbTUI-lkpEv5sTW7ivxs'
genai.configure(api_key=GEMINI_API_KEY)

# שימוש בשם המודל הסטנדרטי ביותר
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/test', methods=['GET', 'POST'])
def test():
    file_path = request.values.get('val')
    print(f"DEBUG: Received file path: {file_path}")

    if not file_path or "%" in str(file_path):
        return Response("id_list_message=t-נא להקליט הודעה לאחר הצליל", mimetype='text/plain')

    try:
        # בניית כתובת ההורדה שעבדה לנו בלוגים
        full_url = f"https://call2all.co.il/ym/api/DownloadFile?path=ivr2/{file_path}"
        print(f"DEBUG: Attempting to download from: {full_url}")
        
        response_audio = requests.get(full_url, timeout=15)
        response_audio.raise_for_status()
        
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # העלאת הקובץ לגוגל
        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        
        # בקשת תשובה
        response = model.generate_content([
            sample_file,
            "הקשב להקלטה וענה עליה בקצרה מאוד בעברית (עד 20 מילים)."
        ])
        
        # ניקוי הטקסט עבור ימות המשיח
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        print(f"Gemini response: {clean_text}")
        
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"Detailed Error: {str(e)}")
        # אם יש שגיאה של "מודל לא נמצא", ננסה להחזיר אותה לטלפון כדי שתדע
        return Response(f"id_list_message=t-חלה שגיאה בעיבוד {str(e)[:20]}", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

