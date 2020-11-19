FROM python:3

RUN git clone https://github.com/moozeq/CP_BenOne.git

WORKDIR /CP_BenOne

RUN pip3 install -r requirements.txt
RUN cp docs/docker_cfg.json ./cfg.json

ENTRYPOINT [ "python3" ]
CMD ["benone.py", "-c", "cfg.json"]