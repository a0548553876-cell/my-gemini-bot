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
    # ימות המשיח שולחים את נתיב ההקלטה במשתנה בשם val
    file_path = request.values.get('val')
    
    # הדפסה ללוגים כדי שנוכל לראות את הנתיב שהתקבל
    print(f"DEBUG: Received file path from Yemot: {file_path}")

    if not file_path or "%" in str(file_path):
        return Response("id_list_message=t-נא להקליט הודעה לאחר הצליל", mimetype='text/plain')

    try:
        # בניית הלינק המלא להורדה מהשרת של ימות המשיח
        download_url = f"https://call2all.co.il/ym/api/DownloadFile?token=YOUR_TOKEN&path={file_path}"
        # הערה: אם המערכת שלך פתוחה ללא טוקן, הלינק עשוי להשתנות. 
        # אבל בוא ננסה קודם לראות אם ג'מיני מצליח לקרוא את הקובץ.
        
        response_audio = requests.get(file_path, timeout=15)
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        sample_file = genai.upload_file(path="temp_audio.wav", mime_type="audio/wav")
        response = model.generate_content([sample_file, "ענה בקצרה בעברית על ההקלטה"])
        
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(f"id_list_message=t-שגיאה בעיבוד הקובץ", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
