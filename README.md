# BenOne

Flask based application for examining Benford's Law of provided file.

# Docker

```bash
git clone https://github.com/moozeq/CP_BenOne.git

docker build -t python-ben CP_BenOne
docker run --name run_docker_run -d -p 5000:5000 python-ben
```

App should be available at [127.0.0.1:5000](http://127.0.0.1:5000)

# Development

```bash
git clone https://github.com/moozeq/CP_BenOne.git
cd CP_BenOne
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# copy simple config file
cp docs/simple_cfg.json ./cfg.json

# run app
./benone.py -c cfg.json
```

App should be available at [127.0.0.1:5000](http://127.0.0.1:5000)