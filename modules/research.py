import PySimpleGUI as sg
import requests
import os

api_key = 'your_api_key'
endpoint = 'your_endpoint_url'


def chatgpt_api_request(query):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    data = {
        'input': query,
    }
    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()['output']


def process_keywords(file=None, keyword=None):
    if file:
        with open(file, 'r') as f:
            keywords = [line.strip() for line in f.readlines()]
    else:
        keywords = [keyword]

    result = []
    for kw in keywords:
        response = chatgpt_api_request(kw)
        result.extend(response.split(','))
    return ', '.join(result)


layout = [
    [sg.Text('Keyword or Text File with Keywords')],
    [sg.InputText(key='keyword_input'), sg.FileBrowse(file_types=(("Text Files", "*.txt"),))],
    [sg.Button('Generate Keywords')],
    [sg.Text('Output')],
    [sg.Output(size=(60, 20), key='output_area')],
]

window = sg.Window('Content Research Tool', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Generate Keywords':
        keyword = values['keyword_input']
        file = values['Browse']
        print(keyword)
        if file and os.path.isfile(file):
            window['output_area'].update(f"File: {file}\n")
            output = process_keywords(file=file)
        else:
            window['output_area'].update(f"Keyword: {keyword}\n")
            output = process_keywords(keyword=keyword)
        window['output_area'].print(output)

window.close()
