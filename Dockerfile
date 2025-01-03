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

# Copiar o arquivo de configuração do OpenSIPS
COPY cfg/opensips.cfg /usr/local/etc/opensips/opensips.cfg

# Copiar o código-fonte para o contêiner
COPY app.py .

# Expor a porta que o Flask vai usar
EXPOSE 5060

# Comando para rodar o aplicativo
CMD ["python", "app.py"]
