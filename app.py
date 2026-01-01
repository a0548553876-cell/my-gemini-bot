import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# וודא שהמפתח החדש שלך כאן ללא רווחים
GEMINI_API_KEY = 'AIzaSyCrzRKa84LkocOiF0dkC3wx1O_IVJfDGug'
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/test', methods=['GET', 'POST'])
def test():
    file_path = request.values.get('val')
    print(f"DEBUG: Processing file: {file_path}")

    if not file_path or "%" in str(file_path):
        return Response("id_list_message=t-נא להקליט הודעה לאחר הצליל", mimetype='text/plain')

    try:
        # בניית כתובת ההורדה
        full_url = f"https://call2all.co.il/ym/api/DownloadFile?path=ivr2/{file_path}"
        response_audio = requests.get(full_url, timeout=15)
        response_audio.raise_for_status()
        
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # יצירת המודל עם הגדרה מפורשת למניעת 404
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        
        # העלאה וניתוח
        audio_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        response = model.generate_content([audio_file, "ענה בקצרה מאוד בעברית על ההקלטה (עד 15 מילים)."])
        
        # ניקוי התשובה עבור ימות המשיח
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        print(f"DEBUG: Gemini Response: {clean_text}")
        
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        error_msg = str(e)
        print(f"CRITICAL ERROR: {error_msg}")
        # החזרת קוד השגיאה לטלפון כדי שנדע מה קורה
        short_error = error_msg[:20].replace(" ", "_")
        return Response(f"id_list_message=t-חלה שגיאה {short_error}", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
