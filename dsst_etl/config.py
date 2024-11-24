from dotenv import dotenv_values


class Config:
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            setattr(self, key, value)


# Load the environment variables from the .env file
config = Config(dotenv_values(".env"))
