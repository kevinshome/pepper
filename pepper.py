import os
import sys
import inspect
import shutil
import webbrowser
import multiprocessing
from textwrap import TextWrapper
from urllib.request import urlopen, HTTPError
from http.client import HTTPResponse
from html.parser import HTMLParser

__version__ = "0.0.0"
RAW_PEP_URL_BASE = "https://raw.githubusercontent.com/python/peps/main/pep-"
PEP_URL_BASE = "https://peps.python.org/pep-"
PEP_0_URL = "https://peps.python.org/pep-0000"

try:
    WEBVIEW = __import__("webview")
except ModuleNotFoundError:
    WEBVIEW = None

PEP_TYPES = {
    "Informational": ("I", "Non-normative PEP containing background, guidelines or other information relevant to the Python ecosystem"),
    "Process": ("P", "Normative PEP describing or proposing a change to a Python community process, workflow or governance"),
    "Standards Track": ("S", "Normative PEP with a new feature for Python, implementation change for CPython or interoperability standard for the ecosystem")
}
PEP_STATUSES = {
    "Accepted": ("A", "Normative proposal accepted for implementation"),
    "Active": ("A", "Currently valid informational guidance, or an in-use process"),
    "Deferred": ("D", "Inactive draft that may be taken up again at a later time"),
    "Final": ("F", "Accepted and implementation complete, or no longer active"),
    "Provisional": ("P", "Provisionally accepted but additional feedback needed"),
    "Rejected": ("R", "Formally declined and will not be accepted"),
    "Superseded": ("S", "Replaced by another succeeding PEP"),
    "Withdrawn": ("W", "Removed from consideration by sponsor or authors"),
    "Draft": ("<No Letter>", "Proposal under active discussion and revision")
}

class KeyTextWrapper(TextWrapper):
    def __init__(self, offset_size: int = 0, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.width = shutil.get_terminal_size().columns - offset_size
        self.subsequent_indent = (' '*offset_size)
        self.break_long_words = False
        self.break_on_hyphens = False
        self.max_lines = 4

class PepZeroParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._last_tag = None
        self._current_tag = None
        self._current_attrs = None
        self._read_head = False
        self.parsed_data = []
        self._current_pep = {}
        self._current_pep_col = 0

    def handle_starttag(self, tag, attrs) -> None:
        self._last_tag = self._current_tag
        self._current_tag = tag
        self._current_attrs = attrs
    def handle_data(self, data) -> None:
        if self._current_tag == "section":
            for attr, value in self._current_attrs:
                if attr == "id" and value == "numerical-index":
                    self._read_head = True
                    return
            return
        if not self._read_head:
            return
        if self._last_tag == "td" and self._current_tag == "abbr":
            self._current_tag = None
            for attr, value in self._current_attrs:
                if attr == "title" and value.split(', ')[0] in PEP_TYPES:
                    _type, _status = value.split(', ')
                    self._current_pep["type"] = _type
                    self._current_pep["status"] = _status
                    self._current_pep_col += 2
                    return
        if self._last_tag == "td" and self._current_tag == "a":
            self._current_tag = None
            if self._current_pep_col == 2: # number
                self._current_pep["number"] = int(data)
                self._current_pep_col += 1
            else: # title
                self._current_pep["title"] = data
                self._current_pep_col += 1
        if self._current_tag == "td" and self._current_pep_col == 4:
            self._current_tag = None
            self._current_pep["authors"] = []
            for author in data.split(','):
                self._current_pep["authors"].append(author.strip())
            self._current_pep_col = 0
            self.parsed_data.append(self._current_pep)
            self._current_pep = {}
    def handle_endtag(self, tag) -> None:
        if tag == "section" and self._read_head:
            self._read_head = False
    @classmethod
    def parse(cls, data: bytes) -> dict:
        parser = cls()
        parser.feed(data.decode(errors='xmlcharrefreplace'))
        return parser.parsed_data

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
            self._current_tag = None
            if data == "Discourse thread":
                for attr,value in self._current_attrs:
                    if attr == "href":
                        self.parsed_data[self._last_key] = value
                        return
            if data == "Discourse message":
                for attr,value in self._current_attrs:
                    if attr == "href":
                        self.parsed_data[self._last_key] = value
                        return
            self._list_head = True
            self.parsed_data[self._last_key] = []
        if self._list_head:
            if data == ",\n" or data == "\n":
                return
            self.parsed_data[self._last_key].append(data)
    def handle_endtag(self, tag) -> None:
        if tag == "dd":
            self._list_head = False
    @classmethod
    def parse(cls, data: bytes) -> dict:
        full_parsed_data = {}
        decoded_data = data.decode(errors='xmlcharrefreplace')

        # parse PEP header information
        head_parser = cls()
        head_parser.feed(decoded_data)
        head_parser.parsed_data["Author"] = head_parser.parsed_data["Author"].split(', ')
        full_parsed_data["raw_title"] = head_parser.parsed_data.pop("raw_title")
        full_parsed_data["title"] = head_parser.parsed_data.pop("title")
        full_parsed_data["number"] = head_parser.parsed_data.pop("number")
        full_parsed_data["header"] = head_parser.parsed_data
        return full_parsed_data

def fatal_error(message: str) -> None:
    sys.stderr.write('pepper: ' + message + '\n')
    raise SystemExit(1)

def format_searched_pep(pep_obj: dict) -> str:
    _string = ""

    _string += pep_obj["type"][0]
    _string += pep_obj["status"][0]
    _string += " | "
    _string += str(pep_obj["number"])
    _string += " | "
    _string += pep_obj["title"]
    _string += " | "
    _string += ", ".join(pep_obj["authors"])

    return _string

def _view_helper(pep_id, url):
    WEBVIEW.create_window(
        f'PEP {pep_id}', 
        url, 
        height=800, 
        frameless=True
    )
    WEBVIEW.start()

class Commands:
    def help(_):
        sys.stderr.write(
            f"pepper, version {__version__}\n"
            "Get information about any PEP (Python Enhancement Proposal)\n"
            "\n"
            "usage: pepper [COMMAND] [ARGS]\n"
            "\n"
            "    info [PEP_NUMBER]: get basic info about the specified PEP\n"
            "    search [ATTR] [QUERY]: search for a PEP (searches for QUERY in ATTR)\n"
            "    keys: print the PEP Types and PEP Status keys, taken from PEP 0\n"
            "    view [PEP_NUMBER]: view PEP in webview window (requires webview extra)\n"
            "    open [PEP_NUMBER]: open PEP in your default web browser\n"
            "    help: print this help message\n"
        )
        return 0

    @staticmethod
    def _get_pep_url(pep_id: str):
        url = PEP_URL_BASE + pep_id.zfill(4)

        # assert PEP is valid and site works
        try:
            urlopen(url)
        except HTTPError as exc:
            if exc.status == 404:
                fatal_error(f"PEP {pep_id} not found...")
            fatal_error(f"Recieved error status code '{exc.status}' from peps.python.org")

        return url

    def view(self, pep_id: str):
        pep_url = self._get_pep_url(pep_id)
        print(f"Pulling up PEP {pep_id} in a new window...")
        proc = multiprocessing.Process(target=_view_helper, args=(pep_id, pep_url), daemon=False)
        proc.start()
        print(f"PEP {pep_id} loaded ({proc.pid}), Bye!")
        os._exit(0) # we call os._exit here to ensure the webview stays alive as an orphan, instead of dying along with the parent

    def open(self, pep_id: str):
        pep_url = self._get_pep_url(pep_id)
        print(f"Pulling up PEP {pep_id} in your default browser...")
        webbrowser.open(pep_url, 2)
        print(f"PEP {pep_id} loaded, Bye!")
        return 0

    def keys(_):
        sys.stdout.write('\n')
        print("PEP Types Key")
        print("------------------")
        for title, info in PEP_TYPES.items():
            pad_length = 7+len(title)
            print(f"{title} ({info[0]}) - {KeyTextWrapper(pad_length).fill(info[1])}")
        print("PEP Status Key")
        print("------------------")
        for title, info in PEP_STATUSES.items():
            pad_length = 6+len(title)+len(info[0])
            print(f"{title} ({info[0]}) - {KeyTextWrapper(pad_length).fill(info[1])}")
        sys.stdout.write('\n')
        return 0

    def info(_, pep_id: str):
        try:
            res: HTTPResponse = urlopen(PEP_URL_BASE + pep_id.zfill(4))
        except HTTPError as exc:
            if exc.status == 404:
                fatal_error(f"PEP {pep_id} not found...")
            fatal_error(f"Recieved error status code '{exc.status}' from peps.python.org")

        parsed_pep = PepFileHeaderParser.parse(res.read())
        print(parsed_pep["raw_title"])
        print(f"({PEP_URL_BASE + pep_id.zfill(4)})", end='\n\n')
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
    
    def search(_, attribute, *query_list):
        
        try:
            res: HTTPResponse = urlopen(PEP_0_URL)
        except HTTPError as exc:
            fatal_error(f"Recieved error status code '{exc.status}' from python.org")

        parsed_list = PepZeroParser.parse(res.read())
        if parsed_list[0].get(attribute.lower()) is None:
            fatal_error(f"Invalid attribute: '{attribute}'")

        for query in query_list:
            print(f"\nResults for '{attribute}' query: '{query}'")
            peps = []
            for pep in parsed_list:
                if attribute == "authors":
                    if query.lower() in [x.lower() for x in pep[attribute]]:
                        peps.append(format_searched_pep(pep))
                else:
                    if query.lower() in str(pep[attribute]).lower():
                        peps.append(format_searched_pep(pep))
            if not peps:
                sys.stderr.write(f"No PEP found matching the following query: '{query}'\n")
                return 1

            print("---------------------------------------")
            print("| Type/Status | PEP | Title | Authors |")
            print("---------------------------------------\n")
            for pep in peps:
                print(pep)

        sys.stdout.write('\n')
        return 0

    def run_cmd(self, cmd, args):
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        func = None
        for name, ref in members:
            if cmd == name:
                func = ref
        if func is None or func.__name__ == "run_cmd":
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
