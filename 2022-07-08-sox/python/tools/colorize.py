try:
    from colorama import Fore
except ImportError:
    class Fore:
        BLUE = ""
        MAGENTA = ""
        GREEN = ""
        RED = ""
        CYAN = ""
        YELLOW = ""
        RESET = ""

def printdict(d,space=0):
    if space == 0:
        color = Fore.BLUE
    elif space == 2:
        color = Fore.MAGENTA
    else:
        color = Fore.GREEN

    for k,v in d.items():
        print(f"{' '*space}{color}{k}:{Fore.RESET}")
        if isinstance(v, dict):
            printdict(v, space+2)
        elif isinstance(v, tuple):
            for i in v:
                print(f"{' '*(space+2)}{i}")
        else:
            print(f"{' '*(space+2)}{v}")