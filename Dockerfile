# Usar uma imagem base do Python
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Criar os diretórios necessários
RUN mkdir -p /app/audio /usr/local/etc/opensips

# Criar o arquivo opensips.cfg
RUN echo '# Configurações globais\n\
debug=3\n\
log_stderror=yes\n\
log_facility=LOG_LOCAL0\n\
\n\
# Módulos a serem carregados\n\
loadmodule "signaling.so"\n\
loadmodule "sl.so"\n\
loadmodule "tm.so"\n\
loadmodule "rr.so"\n\
loadmodule "maxfwd.so"\n\
loadmodule "textops.so"\n\
loadmodule "sipmsgops.so"\n\
loadmodule "xlog.so"\n\
loadmodule "sanity.so"\n\
loadmodule "ctl.so"\n\
loadmodule "mi_fifo.so"\n\
loadmodule "acc.so"\n\
loadmodule "dialog.so"\n\
loadmodule "dispatcher.so"\n\
loadmodule "rtpengine.so"\n\
\n\
# Configuração do socket\n\
listen=udp:0.0.0.0:5060\n\
\n\
# Roteamento básico\n\
route {\n\
    # Verifica o número máximo de encaminhamentos\n\
    if (!mf_process_maxfwd_header("10")) {\n\
        sl_send_reply("483", "Too Many Hops");\n\
        exit;\n\
    }\n\
\n\
    # Verifica a sanidade da mensagem SIP\n\
    if (!sanity_check("1511", "7")) {\n\
        sl_send_reply("400", "Bad Request");\n\
        exit;\n\
    }\n\
\n\
    # Roteia a chamada para o endpoint do Flask\n\
    if ($rU == "suporte" || $rU == "vendas") {\n\
        $du = "sip:app:5060";  # Encaminha para o serviço Flask\n\
        t_relay();\n\
        exit;\n\
    }\n\
\n\
    # Responde para números desconhecidos\n\
    sl_send_reply("404", "Not Found");\n\
}\n' > /usr/local/etc/opensips/opensips.cfg

# Copiar o código-fonte para o contêiner
COPY app.py .

# Expor a porta que o Flask vai usar
EXPOSE 5060

# Comando para rodar o aplicativo
CMD ["python", "app.py"]
