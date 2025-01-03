from flask import Flask, request, jsonify
from deepgram import Deepgram
import asyncio
import openai
from gtts import gTTS
import os

app = Flask(__name__)

DEEPGRAM_API_KEY = ''
OPENAI_API_KEY = ''

async def transcribe_audio(audio_url):
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    source = {'url': audio_url}
    response = await deepgram.transcription.prerecorded(source, {'punctuate': True})
    return response['results']['channels'][0]['alternatives'][0]['transcript']

def generate_response(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def text_to_speech(text, output_file='output.mp3'):
    tts = gTTS(text=text, lang='pt')
    tts.save(output_file)
    return output_file

def route_call(caller, callee):
    if callee == "suporte":
        return "Você será conectado ao suporte técnico."
    elif callee == "vendas":
        return "Você será conectado ao departamento de vendas."
    else:
        return "Desculpe, não reconhecemos o número discado."

@app.route('/sip/call', methods=['POST'])
def handle_call():
    data = request.json
    caller = data.get('caller')
    callee = data.get('callee')
    audio_url = data.get('audio_url')

    # Transcrever áudio
    transcription = asyncio.run(transcribe_audio(audio_url))
    print(f"Transcrição: {transcription}")

    # Gerar resposta com OpenAI
    response_text = generate_response(transcription)
    print(f"Resposta gerada: {response_text}")

    # Converter resposta em áudio
    audio_file = text_to_speech(response_text)
    print(f"Áudio gerado: {audio_file}")

    # Roteamento de chamada
    routing_response = route_call(caller, callee)
    print(f"Roteamento: {routing_response}")

    # Retornar resposta
    return jsonify({
        "status": "processed",
        "transcription": transcription,
        "response": response_text,
        "audio_file": audio_file,
        "routing_response": routing_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5060)
