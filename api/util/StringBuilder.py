from cStringIO import StringIO


class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = StringIO()

    def append(self, line):
        self._file_str.write(line + "\n")

    def __str__(self):
        return self._file_str.getvalue()