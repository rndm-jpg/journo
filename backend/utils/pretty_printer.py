class PrettyColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _print_with_color(color, tag, text):
    try:
        print(f"{color}{tag}{PrettyColors.ENDC}: {text}")
    except:
        print("Unprintable text")


def print_primary(tag, text):
    _print_with_color(PrettyColors.OKBLUE, tag, text)


def print_warning(tag, text):
    _print_with_color(PrettyColors.WARNING, tag, text)


def print_success(tag, text):
    _print_with_color(PrettyColors.OKGREEN, tag, text)


def print_danger(tag, text):
    _print_with_color(PrettyColors.FAIL, tag, text)
