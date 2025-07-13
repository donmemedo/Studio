FROM python:3.12

ENV TZ=Asia/Tehran

COPY . /app

WORKDIR /app

RUN pip install -U pip
RUN pip install -r requirements.txt

RUN ls

ENV PYTHONPATH="$PYTHONPATH:/app"

WORKDIR /app/src

EXPOSE 8000

CMD python main.py