import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# הגדרת מפתח ה-API ללא רווחים
GEMINI_API_KEY = 'AIzaSyCrzRKa84LkocOiF0dkC3wx1O_IVJfDGug'
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/test', methods=['GET', 'POST'])
def test():
    file_path = request.values.get('val')
    print(f"DEBUG: Received path: {file_path}")

    if not file_path or "%" in str(file_path):
        return Response("id_list_message=t-נא להקליט הודעה לאחר הצליל", mimetype='text/plain')

    try:
        # הורדת הקובץ מימות המשיח
        full_url = f"https://call2all.co.il/ym/api/DownloadFile?path=ivr2/{file_path}"
        response_audio = requests.get(full_url, timeout=15)
        response_audio.raise_for_status()
        
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # יצירת המודל (שימוש בשם הבסיסי והיציב ביותר)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # העלאה לגוגל
        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        
        # קבלת תשובה
        response = model.generate_content([
            sample_file,
            "ענה בקצרה מאוד בעברית על ההקלטה."
        ])
        
        # ניקוי הטקסט עבור ימות המשיח
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        print(f"DEBUG: Gemini response: {clean_text}")
        
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"Detailed Error: {str(e)}")
        return Response(f"id_list_message=t-שגיאה {str(e)[:15]}", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


