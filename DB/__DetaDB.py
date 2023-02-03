from deta import Deta
import configparser

class DataBase:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('secret_key.ini')
        return Deta(config["database"]["project_key"])