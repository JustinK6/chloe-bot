FROM python:3.8

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

VOLUME /data

EXPOSE 5000

CMD ["python", "bot.py"]