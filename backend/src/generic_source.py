import inspect

from utils.helper import print_json
from utils.pretty_printer import print_primary, print_success


class GenericSource:
    @staticmethod
    def print_primary(source_name, tag, text):
        print_primary(f"{source_name} => {tag}", text)

    @staticmethod
    def print_success(source_name, tag, text):
        print_success(f"{source_name} => {tag}", text)
