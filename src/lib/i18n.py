import yaml
from os import getcwd
import pdb

from src import cfg


class Message:
    def __init__(self, lang: str = None) -> None:
        if lang is None:
            lang = cfg["app"]["default_locale"]
        self.locale_exists = True
        try:
            with open(f"{getcwd()}/src/i18n/{lang.replace('_', '-')}.yaml", "r") as stream:
                self.dictionary = yaml.safe_load(stream)
        
        except FileNotFoundError:
            self.locale_exists = False
            with open(f"{getcwd()}/src/i18n/{cfg['app']['default_locale']}.yaml", "r") as stream:
                self.dictionary = yaml.safe_load(stream)
        
        except yaml.YAMLError as exc:
            print(exc)

    def get(self, msg: str):
        # pdb.set_trace()
        if not self.locale_exists:
            return self.dictionary["locale"]["not_found"]
    
        new_level = self.dictionary
        for level in msg.split("."):
            new_level = new_level[level]
            if level == msg.split(".")[-1]:
                return new_level
        
        return "[ERROR] Appropriate message not found"
