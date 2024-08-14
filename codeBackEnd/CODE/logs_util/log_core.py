import datetime, os


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


class LogCore:
    """
        small class that helps with loging messages
        @ source_file: 
            the source of the log(best practice to pass the name of the file the class is initiated in)
        @ txtfile_friendly:
            True : logs the msg as it is
            False : adds color to it, to make it easy to read,
                    if you're intending on reading the file from
                    a terminal.
    """
    __EXCEPTIONS_FILE_NAME = "exceptions.txt"
    __INFO_FILE_NAME = "info.txt"
    __ROOTINE_FILE_NAME = "rootine.txt"

    def __init__(self, source_file: str, txtfile_friendly: bool):
        self.source_file = source_file
        self.txtfile_friendly = txtfile_friendly

    def writer(self, file_name: str, content: str):
        with open("logs_util/" + file_name, "a") as file:
            file.write(content+'\n')


    def log_exception(self, content: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_format = None
        if self.txtfile_friendly:
            log_format = f"[{date}]({self.source_file}): {content}"
        else:
            log_format = f"[{Colors.GREEN}{date}{Colors.RESET}]({Colors.YELLOW}{self.source_file}{Colors.RESET}):{Colors.RED} {content}{Colors.RESET}"
        self.writer(file_name=LogCore.__EXCEPTIONS_FILE_NAME, content=log_format)

    def log_info(self, content: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_format = None
        if self.txtfile_friendly:
            log_format = f"[{date}]({self.source_file}): {content}"
        else:
            log_format = f"[{Colors.GREEN}{date}{Colors.RESET}]({Colors.YELLOW}{self.source_file}{Colors.RESET}):{Colors.BLUE} {content}{Colors.RESET}"
        self.writer(file_name=LogCore.__INFO_FILE_NAME, content=log_format)

    def log_rootin(self, content: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_format = None
        if self.txtfile_friendly:
            log_format = f"[{date}]({self.source_file}): {content}"
        else:
            log_format = f"[{Colors.GREEN}{date}{Colors.RESET}]({Colors.YELLOW}{self.source_file}{Colors.RESET}):{Colors.GREEN} {content}{Colors.RESET}"
        self.writer(file_name=LogCore.__ROOTINE_FILE_NAME, content=log_format)
