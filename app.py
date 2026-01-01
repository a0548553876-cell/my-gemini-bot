import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response
import re

app = Flask(__name__)

# וודא שהמפתח כאן תקין וללא רווחים
GEMINI_API_KEY = 'AIzaSyCrzRKa84LkocOiF0dkC3wx1O_IVJfDGug'
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/test', methods=['GET', 'POST'])
def test():
    file_path = request.values.get('val')
    if not file_path:
        return Response("id_list_message=t-נא להקליט הודעה", mimetype='text/plain')

    try:
        # הורדת הקובץ
        full_url = f"https://call2all.co.il/ym/api/DownloadFile?path=ivr2/{file_path}"
        response_audio = requests.get(full_url, timeout=15)
        response_audio.raise_for_status()
        
        with open("temp_audio.wav", "wb") as f:
            f.write(response_audio.content)

        model = genai.GenerativeModel("gemini-1.5-flash")
        audio_file = genai.upload_file(path="temp_audio.wav")
        
        # שינוי ההנחיה לתשובה מפורטת
        response = model.generate_content([
            audio_file, 
            "נתח את ההקלטה וענה עליה בצורה מפורטת מאוד בעברית. הסבר את כל הנקודות החשובות."
        ])
        
        clean_text = re.sub(r'[^\u0590-\u05FF\s0-9.,?!]', '', response.text).strip()
        print(f"DEBUG Response: {clean_text}") # תוכל לראות את זה בלוג ב-Render
        
        return Response(f"id_list_message=t-{clean_text}", mimetype='text/plain')

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return Response(f"id_list_message=t-חלה שגיאה בעיבוד", mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
