# BenOne

Flask based application for examining Benford's Law of provided files.

# Docker

```bash
docker build -t python-ben github.com/moozeq/ben-one
docker run --name run_docker_run -d -p 5000:5000 python-ben
```

App should be available at [127.0.0.1:5000](http://127.0.0.1:5000)

# Development

```bash
git clone https://github.com/moozeq/ben-one.git

# prepare environment
cd ben-one
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# copy docker config file or create your own
cp docs/docker_cfg.json ./cfg.json

# run app
./benone.py -c cfg.json
```

App should be available at [127.0.0.1:5000](http://127.0.0.1:5000)
