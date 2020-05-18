FROM python:3.7

RUN mkdir /code
WORKDIR /code
COPY * . ./
RUN pip install -r requirements.txt
ENTRYPOINT python app.py
