class Term:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def error(msg: str):
        print(f'{Term.FAIL}[ERROR] {msg}{Term.ENDC}')

    @staticmethod
    def ok(msg: str):
        print(f'{Term.OKGREEN}[OK] {msg}{Term.ENDC}')

    @staticmethod
    def info(msg: str):
        print(f'[INFO] {msg}')