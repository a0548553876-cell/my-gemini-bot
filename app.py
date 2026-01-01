import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# וודא שהמפתח מועתק בדיוק, בלי רווחים בתוך המרכאות!
GEMINI_API_KEY = 'AIzaSyA6M5Y3_ajzoUGcbTUI-lkpEv5sTW7ivxs'
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/test', methods=['GET', 'POST'])
def test():
    file_path = request.values.get('val')
    
    if not file_path or "%" in str(file_path):
        return Response("id_list_message=t-נא להקליט הודעה לאחר הצליל", mimetype='text/plain')

    try:
        # בניית הכתובת שעובדת (כפי שראינו בלוגים)
        full_url = f"https://call2all.co.il/ym/api/DownloadFile?path=ivr2/{file_path}"
        
        response_audio = requests.get(full_url, timeout=15)
        response_audio.raise_for_status()
        
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # יצירת המודל בתוך הפונקציה כדי לוודא רענון
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # העלאה ועיבוד
        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        response = model.generate_content([
            sample_file,
            "הקשב להקלטה וענה עליה בקצרה מאוד בעברית (עד 20 מילים)."
        ])
        
        # ניקוי הטקסט
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        print(f"DEBUG: Gemini said: {clean_text}")
        
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"Detailed Error: {str(e)}")
        # מחזיר את תחילת השגיאה לטלפון כדי שנדע אם המפתח עדיין בעייתי
        return Response(f"id_list_message=t-שגיאה {str(e)[:15]}", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
