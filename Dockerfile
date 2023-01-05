FROM python:3

RUN git clone https://github.com/moozeq/ben-one.git

WORKDIR /ben-one

RUN pip3 install -r requirements.txt
RUN cp docs/docker_cfg.json ./cfg.json
RUN python3 -m unittest discover tests

ENTRYPOINT [ "gunicorn" ]

CMD ["--threads=8", "--worker-class=gthread", "--bind=0.0.0.0:5000", "benone:create_app()"]
