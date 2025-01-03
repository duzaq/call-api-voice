import asyncio
import logging
import os

import openai
from deepgram import Deepgram
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from gtts import gTTS

# Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Carregar chaves de API do ambiente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
if not OPENAI_API_KEY or not DEEPGRAM_API_KEY:
    logging.error("Variáveis de ambiente OPENAI_API_KEY ou DEEPGRAM_API_KEY não estão definidas.")
    exit(1)

# Inicializar cliente Deepgram
try:
    deepgram = Deepgram(DEEPGRAM_API_KEY)
except Exception as e:
    logging.error(f"Erro ao inicializar o cliente Deepgram: {e}")
    exit(1)

async def transcribe_audio(audio_url):
    """
    Transcreve áudio de uma URL usando a API do Deepgram.

    Args:
        audio_url: A URL do arquivo de áudio.

    Returns:
        A transcrição do áudio, ou uma string vazia em caso de erro.
    """
    try:
        source = {'url': audio_url}
        logging.info(f"Transcrevendo áudio da URL: {audio_url}")
        response = await deepgram.transcription.prerecorded(source, {'punctuate': True, 'utterances': True}) # adicionando o utterances, que é mais preciso para identificar a fala
        logging.info("Áudio transcrito com sucesso.")
        # Verificando se a resposta contém a estrutura esperada
        if 'results' in response and 'channels' in response['results']:
            transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
            return transcript
        else:
            logging.warning("Resposta da Deepgram em formato inesperado.")
            return ""
    except Exception as e:
        logging.error(f"Erro ao transcrever áudio: {e}")
        return ""

def generate_response(prompt):
    """
    Gera uma resposta usando a API da OpenAI.

    Args:
        prompt: O prompt para a API.

    Returns:
        A resposta gerada pela API, ou uma mensagem de erro em caso de falha.
    """
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        result = response['choices'][0]['message']['content'].strip()
        logging.info("Resposta gerada com sucesso pela OpenAI.")
        return result
    except Exception as e:
        logging.error(f"Erro ao gerar resposta com OpenAI: {e}")
        return "Desculpe, não consegui gerar uma resposta no momento."

def text_to_speech(text, output_file='output.mp3'):
    """
    Converte texto em fala usando gTTS.

    Args:
        text: O texto a ser convertido.
        output_file: O nome do arquivo de saída.

    Returns:
        O nome do arquivo de saída.
    """
    try:
        tts = gTTS(text=text, lang='pt')
        tts.save(output_file)
        logging.info(f"Texto convertido em áudio e salvo em {output_file}")
        return output_file
    except Exception as e:
        logging.error(f"Erro ao converter texto em áudio: {e}")
        return ""

def route_call(callee):
    """
    Simula o roteamento de chamadas com base no número discado.

    Args:
        callee: O número discado.

    Returns:
        Uma mensagem indicando o destino da chamada.
    """
    if callee == "suporte":
        logging.info("Chamada roteada para o suporte técnico.")
        return "Você será conectado ao suporte técnico."
    elif callee == "vendas":
        logging.info("Chamada roteada para o departamento de vendas.")
        return "Você será conectado ao departamento de vendas."
    else:
        logging.warning(f"Número discado desconhecido: {callee}")
        return "Desculpe, não reconhecemos o número discado."

@app.route('/sip/call', methods=['POST'])
async def handle_call():
    """
    Lida com as chamadas SIP, transcrevendo áudio, gerando respostas e simulando roteamento.
    """
    try:
        data = request.json
        # Validar entrada
        if not data or 'caller' not in data or 'callee' not in data or 'audio_url' not in data:
            logging.warning("Requisição inválida: dados incompletos.")
            return jsonify({"error": "Requisição inválida: dados incompletos."}), 400

        caller = data['caller']
        callee = data['callee']
        audio_url = data['audio_url']

        logging.info(f"Recebida chamada de {caller} para {callee}, áudio URL: {audio_url}")

        # Transcrever áudio
        transcription = await transcribe_audio(audio_url)
        if not transcription:
            return jsonify({"error": "Erro ao transcrever áudio."}), 500

        # Gerar resposta com OpenAI
        response_text = generate_response(transcription)

        # Converter resposta em áudio
        audio_file = text_to_speech(response_text)
        if not audio_file:
            return jsonify({"error": "Erro ao converter resposta em áudio."}), 500

        # Roteamento de chamada
        routing_response = route_call(callee)

        # Retornar resposta
        return jsonify({
            "status": "processed",
            "transcription": transcription,
            "response": response_text,
            "audio_file": audio_file,
            "routing_response": routing_response
        })

    except Exception as e:
        logging.error(f"Erro inesperado ao processar chamada: {e}")
        return jsonify({"error": "Erro interno do servidor."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5060)))
