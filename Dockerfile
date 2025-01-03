# Usar uma imagem base do Python
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Criar os diretórios necessários
RUN mkdir -p /app/audio

# Não precisamos mais criar /app/cfg e /app/nginx, pois eles serão montados

# Copiar o código-fonte para o contêiner (agora copia o app.py da raiz)
COPY app.py .

# Expor a porta que o Flask vai usar
EXPOSE 5060

# Comando para rodar o aplicativo
CMD ["python", "app.py"]
