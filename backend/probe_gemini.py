import urllib.request
import urllib.error
import json

urls = [
    'https://gemini.googleapis.com/v1/models/gemini-1.5:generate?key=XYZ',
    'https://gemini.googleapis.com/v1/models/gemini-1.5/predict?key=XYZ',
    'https://gemini.googleapis.com/v1/models/gemini-1.5:predict?key=XYZ',
    'https://gemini.googleapis.com/v1/models/gemini-1.5/generate?key=XYZ',
    'https://gemini.googleapis.com/v1/models/gemini-1.5:predict',
    'https://gemini.googleapis.com/v1/models/gemini-1.5:generate',
    'https://gemini.googleapis.com/v1beta2/models/gemini-1.5:generate?key=XYZ',
    'https://gemini.googleapis.com/v1beta2/models/gemini-1.5/generate',
    'https://generativelanguage.googleapis.com/v1/models/gemini-1.5:generate?key=XYZ',
    'https://generativelanguage.googleapis.com/v1/models/gemini-1.5/generate',
    'https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5:generate?key=XYZ',
    'https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5:generate',
]
body = json.dumps({'input': {'text': 'hello'}}).encode('utf-8')

for url in urls:
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    print('URL:', url)
    try:
        response = urllib.request.urlopen(req, timeout=10)
        print('OK', response.status)
        print(response.read().decode('utf-8')[:1000])
    except urllib.error.HTTPError as e:
        print('HTTPError', e.code, e.reason)
        try:
            body = e.read().decode('utf-8', errors='replace')
            print('BODY:', body[:1000])
        except Exception as inner:
            print('BODY READ ERROR', inner)
    except Exception as e:
        print('ERROR', e)
    print('-' * 60)
