import sys
import inspect
from urllib.request import urlopen, HTTPError
from http.client import HTTPResponse
from html.parser import HTMLParser

__version__ = "0.0.0"
RAW_PEP_URL_BASE = "https://raw.githubusercontent.com/python/peps/main/pep-"
PEP_URL_BASE = "https://peps.python.org/pep-"
PEP_0_URL = "https://peps.python.org/pep-0000"

class PepFileHeaderParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self._last_tag = None
            self._current_tag = None
            self._current_attrs = None
            self._last_key = None
            self._list_head = False
            self._title_read = False
            self.parsed_data = {}
        def handle_starttag(self, tag, attrs) -> None:
            self._last_tag = self._current_tag
            self._current_tag = tag
            self._current_attrs = attrs
        def handle_data(self, data) -> None:
            if self._current_tag == "h1" and not self._title_read:
                for attr, value in self._current_attrs:
                    if attr == "class" and value == "page-title":
                        self._title_read = True
                        pep, title = data.split(" – ")
                        self.parsed_data["raw_title"] = data
                        self.parsed_data["title"] = title
                        self.parsed_data["number"] = pep.split()[1]
                        return
            if self._current_tag == "dt":
                self._current_tag = None
                self.parsed_data[data] = ""
                self._last_key = data
            if self._current_tag == "dd":
                self._current_tag = None
                self.parsed_data[self._last_key] = data
            if self._current_tag == "abbr":
                self._current_tag = None
                self.parsed_data[self._last_key] = data
            if self._current_tag == "a" and self._last_tag == "dd":
                self._list_head = True
                self._current_tag = None
                self.parsed_data[self._last_key] = []
            if self._list_head:
                if data == ",\n" or data == "\n":
                    return
                self.parsed_data[self._last_key].append(data)
        def handle_endtag(self, tag) -> None:
            if tag == "dd":
                self._list_head = False

def fatal_error(message: str):
    sys.stderr.write('pepper: ' + message + '\n')
    raise SystemExit(1)

def parse_pepfile_header(data: bytes):
    full_parsed_data = {}
    decoded_data = data.decode(errors='xmlcharrefreplace')

    # parse PEP header information
    head_parser = PepFileHeaderParser()
    head_parser.feed(decoded_data)
    head_parser.parsed_data["Author"] = head_parser.parsed_data["Author"].split(', ')
    head_parser.parsed_data.pop("Discussions-To", None)
    head_parser.parsed_data.pop("Resolution", None)
    full_parsed_data["raw_title"] = head_parser.parsed_data.pop("raw_title")
    full_parsed_data["title"] = head_parser.parsed_data.pop("title")
    full_parsed_data["number"] = head_parser.parsed_data.pop("number")
    full_parsed_data["header"] = head_parser.parsed_data
    return full_parsed_data

class Commands:
    def help(_):
        sys.stderr.write(
            f"pepper, version {__version__}\n"
            "Get information about any PEP (Python Enhancement Proposal)\n"
            "\n"
            "usage: pepper [COMMAND] [ARGS]\n"
            "\n"
            "    info [PEP_NUMBER]: get basic info about the specified PEP\n"
            "    search [QUERY]: search for a PEP (searches for QUERY as substring in title)\n"
            "    help: print this help message\n"
        )
        return 0

    def info(_, pep_id: str):
        try:
            res: HTTPResponse = urlopen(PEP_URL_BASE + pep_id.zfill(4))
        except HTTPError as exc:
            if exc.status == 404:
                fatal_error(f"PEP {pep_id} not found...")
            fatal_error(f"Recieved error status code '{exc.status}' from python.org")

        parsed_pep = parse_pepfile_header(res.read())
        print(parsed_pep["raw_title"], end='\n\n')
        for item in parsed_pep["header"].items():
            print('\t', end='')
            if not isinstance(item[1], list):
                print(': '.join(item))
            elif item[0] == "Author":
                print(f"{item[0]}: {item[1][0]}")
                item[1].pop(0)
                for entry in item[1]:
                    print(f"\t\t{entry}")
            else:
                s = f"{item[0]}: {item[1][0]},"
                item[1].pop(0)
                for entry in item[1]:
                    s += f" {entry},"
                print(s.strip(','))
        return 0
    
    def run_cmd(self, cmd, args):
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        func = None
        for name, ref in members:
            if cmd == name:
                func = ref
        if func is None:
            fatal_error(f"No such command ({cmd})...")
        
        param_count = len(inspect.signature(func).parameters)
        if param_count > len(args):
            fatal_error(f"Not enough arguments (expected {param_count}, got {len(args)}).")
        raise SystemExit(func(*args))

def main():
    if len(sys.argv) == 1:
        Commands().help()
        raise SystemExit(1)
    commands = Commands()
    commands.run_cmd(sys.argv[1], sys.argv[2:])
