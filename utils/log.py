from colorama import Fore


class Logger:

    def success(text):
        print(Fore.GREEN + "[+]", text, Fore.RESET)
    def error(text):
        print(Fore.RED + "[!]", text, Fore.RESET)

    def warn(text):
        print(Fore.YELLOW + "[-]", text, Fore.RESET)

    def info(text):
        print(Fore.BLUE + "[*]", text, Fore.RESET)
