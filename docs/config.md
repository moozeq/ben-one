# Configuration file

Configuration file for BeNone, should be in following format:

|key|description|type|options|default|
|:---:|:---:|:---:|:---:|:---:|
|UPLOAD_FOLDER|directory where users files will be stored|str|any|"data/users_files"|
|ENV|application environment|str|"development", "production"|"production"|
|HOST|application host address|str|any|"127.0.0.1"|
|PORT|application port|int|any|5000|

You can also use [simple_cfg.json](simple_cfg.json), thus there are no
secrets to set up right now.