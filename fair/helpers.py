try:
    # Python 3
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser


class ErdaHTMLArchiveParser(HTMLParser):
    found = None
    result = None

    def __init__(self, identifiers):
        """
        :type identifiers: list of str to be searched for
        Result of the parsing should be saved in self.result. e.g.
        data[identifier] = found value
        """
        super().__init__()
        self.identifiers = identifiers
        self.result = {}


class ErdaHTMLPreTagParser(ErdaHTMLArchiveParser):
    def __init__(self, identifiers):
        """
        :param identifiers: list of strings that should be searched for in
        individual html tag class strings
        """
        super().__init__(identifiers)
        self.found = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            for identity in self.identifiers:
                if identity in value:
                    self.found.append(value)

    def handle_data(self, data):
        if len(self.found) > 0:
            self.result[self.found.pop().split("archive-")[1]] = data

    def handle_endtag(self, tag):
        if len(self.found) < 1 and tag == "pre":
            self.found = []


class ErdaHTMLLegacyParser(ErdaHTMLArchiveParser):
    """
    The identifiers are used as substring identifiers in the html text
    inside a html div container with an attribute of id="content".
    E.g.
    <div class="staticpage" id="content" lang="en">
    <div>
    <h1 class="staticpage">Public Archive</h1>
    This is the public archive with unique ID YXJjaGl2ZS05dHRxRVU= .<br>
    The user-supplied meta data and files are available below.

    <h2 class="staticpage">Archive Meta Data</h2>
    Owner: /C=DK/ST=NA/L=NA/O=NBI/OU=NA/CN=Rasmus Munk/emailAddress=rasmus.munk@nbi.ku.dk<br>
    Name: Rasmus<br>
    Description: Rasmus test<br>
    Date: 2017-09-08 10:05:56.891659<br>
    <h2 class="staticpage">Archive Files</h2>
            <a href="welcome.txt">welcome.txt</a><br>

    </div>
    </div>
    The search itself is case insensitive these are used as key
    Identifiers for the values found in the parsed html.
    Result of the parsing is save in self.result. e.g. data[identifier] =
    found value.
    """

    def __init__(self, identifiers):
        super().__init__(identifiers)
        self.found = False

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" and value == "content":
                self.found = True

    def handle_data(self, data):
        if self.found:
            for tag in self.identifiers:
                noncase_data = data.lower()
                if str.find(noncase_data, tag, 0, len(noncase_data)) != -1:
                    self.result[str(tag)] = " ".join(
                        [
                            tmp_data
                            for tmp_data in data.split()
                            if str.find(tmp_data.lower(), tag, 0, len(tmp_data.lower()))
                            == -1
                        ]
                    )

    def handle_endtag(self, tag):
        if self.found and tag == "div":
            self.found = False
