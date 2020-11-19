# BenOne

Flask based application for examining Benford's Law of provided file.

# Run

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