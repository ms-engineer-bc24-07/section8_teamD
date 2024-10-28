FROM python:3.8

WORKDIR /app
ENV FLASK_APP=app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install --upgrade openai


# ポートの公開
EXPOSE 5000

# コンテナ起動時にapp.pyを実行
CMD ["python", "app.py"]