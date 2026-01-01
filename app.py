import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# וודא שהמפתח כאן ללא רווחים
GEMINI_API_KEY = 'AIzaSyCrzRKa84LkocOiF0dkC3wx1O_IVJfDGug'
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/test', methods=['GET', 'POST'])
def test():
    file_path = request.values.get('val')
    if not file_path:
        return Response("id_list_message=t-נא להקליט הודעה", mimetype='text/plain')

    try:
        # הורדת הקובץ מימות המשיח
        full_url = f"https://call2all.co.il/ym/api/DownloadFile?path=ivr2/{file_path}"
        response_audio = requests.get(full_url, timeout=15)
        response_audio.raise_for_status()
        
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        # הפתרון: שימוש בשם מודל ללא קידומת models/ כדי למנוע 404
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # העלאה
        audio_file = genai.upload_file(path="temp_audio.wav")
        
        # יצירת תשובה
        response = model.generate_content([
            audio_file,
            "הקשב וענה בקצרה מאוד בעברית (עד 10 מילים)."
        ])
        
        # ניקוי הטקסט עבור המערכת הטלפונית
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        # במקרה של שגיאה, נחזיר אותה לטלפון כדי שנדע אם ה-404 נעלם
        error_str = str(e)[:15].replace(" ", "_")
        return Response(f"id_list_message=t-שגיאה_{error_str}", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
