FROM tiangolo/uwsgi-nginx-flask:python3.7-2020-05-09

RUN mkdir /app
WORKDIR /app
COPY * . ./
RUN pip install -r requirements.txt
ENTRYPOINT python app.py
