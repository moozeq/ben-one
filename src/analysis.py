from collections import Counter
from pathlib import Path
from string import digits
from typing import Dict, Union


class WrongFile(Exception):
    """Exception raised when file to analysis does not exist or is corrupted."""

    def __init__(self, path: str, cause: str):
        self.path = path
        if cause == 'not-exists':
            self.message = f'File {path} does not exist'
        elif cause == 'corrupted':
            self.message = f'File {path} is corrupted'
        else:
            self.message = f'File {path} is invalid'

        super().__init__(self.message)


class WrongLetter(Exception):
    """Exception raised when user tries to reference not digit in counter."""

    def __init__(self, letter: str):
        self.message = f'Wrong letter = {letter}, digits allowed only'
        super().__init__(self.message)


class WrongColumn(Exception):
    """Exception raised when user tries to reference to column not in counters dict."""

    def __init__(self, column: str):
        self.message = f'Wrong column = {column}, not exits in counters dictionary'
        super().__init__(self.message)


class Reader:
    """Class for reading from file.

    Args:
        filename (str): path to file to analyze, stored locally
        ext (str): file format, if empty, try recognizing
            by extension
    """

    def __init__(self, filename: str, ext: str = ''):
        self.file = Path(filename)
        if not self.file.exists():
            raise WrongFile(filename, 'not-exists')

        read_funcs = {
            '.csv': Reader.read_csv,
            '.tsv': Reader.read_tsv,
        }

        # if mode provided, use specific function to read file
        if ext in read_funcs:
            self.ext = ext
            self.read_func = read_funcs[ext]
        # if mode not provided, try to recognize file by extension
        else:
            self.ext = self.file.suffix.lower()
            self.read_func = read_funcs.get(self.ext, Reader.read_raw)

    def __iter__(self):
        """Iterating over lines in file.

        Returns:
            next line yielded from file
        """
        yield from self.read_func(self.file)

    @staticmethod
    def read_csv(file: Path):
        import csv
        with file.open(newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            yield from reader

    @staticmethod
    def read_tsv(file: Path):
        import csv
        with file.open(newline='') as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            yield from reader

    @staticmethod
    def read_raw(file: Path):
        with file.open() as file:
            yield from file


class Analysis:
    """Class for reading file with data and analyze digits distributions.
    If possible, digits distributions will be available to analyze per column in data.

    Args:
        filename (str): path to file to analyze, stored locally
        ext (str): file format

    Attributes:
        filename (str): path to file to analyze, stored locally
    """

    def __init__(self, filename: str, ext: str = ''):
        counters, stats = Analysis.analyze_file(filename, ext)
        self._stats = stats
        # convert counters to digit only counters
        self._digit_counters = {
            column: Analysis.to_digit_counter(counter)
            for column, counter in counters.items()
        }
        # merge all counters for whole file analysis and add counter from header which was not included
        self._merged_digit_counter = Analysis.get_merged_digit_counter(self._digit_counters)

    def get_count(self, letter: Union[str, int], column: str = '') -> int:
        """Get letter count for specific column, or if column name not provided - whole file"""
        counter = self.get_counter(column)

        # convert to string if needed
        if isinstance(letter, int):
            letter = str(letter)

        # check if letter in counter
        if letter not in counter:
            raise WrongLetter(letter)
        return counter[letter]

    def get_counter(self, column: str = '') -> Counter:
        """Get counter for specific column, or if column name not provided - whole file"""
        # no column name provided, use merged counter
        if not column:
            counter = self._merged_digit_counter
        else:
            # check if column name in counters
            if column not in self._digit_counters:
                raise WrongColumn(column)
            counter = self._digit_counters[column]
        return counter

    def get_counters(self) -> Dict[str, Counter]:
        return self._digit_counters

    def get_stats(self) -> Dict[str, Union[str, int]]:
        return self._stats

    @staticmethod
    def get_merged_digit_counter(counters: Dict[str, Counter]) -> Counter:
        """Merge all counters"""
        # merge all counters from dict
        merged_counter = sum(counters.values(), Counter())

        # need to add counter for header line
        header_counter = Counter(''.join(counters.keys()))

        # needs to again convert to digit counter
        merged_counter = Analysis.to_digit_counter(merged_counter + header_counter)

        return merged_counter

    @staticmethod
    def to_digit_counter(counter: Counter) -> Counter:
        """Convert letter counter to digit counter"""
        return Counter({
            digit: counter.get(digit, 0)
            for digit in digits
        })

    @staticmethod
    def analyze_file(filename: str, ext: str = '') -> (
            Dict[str, Counter],
            Dict[str, Union[str, int]]):
        """Analyzing file in terms of letters usage.

        For each column in file, getting header and counter for
        this column. Then line by line count letters for each
        column using generators, so even very big files can be
        easily analyze.

        Args:
            filename (str): path to file which will be analyzed
            ext (str): file format, if empty, try recognizing
                by file extension

        Returns:
            1st: dictionary of counters, where keys are columns names
                and values are counters for those columns
            2nd: dictionary with statistics from parsing file
        """

        reader = Reader(filename, ext)
        reader_it = iter(reader)

        # get file header
        header = next(reader_it)

        # create counter for each column in header
        # if header is a single string, treat as one column
        if isinstance(header, str):
            header_len = 1
            counters = [Counter()]
        else:
            header_len = len(header)
            counters = [Counter() for _ in header]

        # iterate over each line, and each element in line
        # count omitted lines
        omitted_lines = 0
        parsed_lines = 0
        parsed_words = 0
        for line in reader_it:
            parsed_lines += 1
            if len(line) != len(header):
                omitted_lines += 1
                # raise WrongFile(filename, 'corrupted')
            for i, elem in enumerate(line):
                parsed_words += 1
                counters[i] += Counter(elem)

        # map counters to header columns
        counters = {
            column: counter
            for column, counter in zip(header, counters)
        }
        stats = {
            'header_size': header_len,
            'omitted_lines': omitted_lines,
            'parsed_lines': parsed_lines,
            'parsed_words': parsed_words,
            'ext': reader.ext,
        }
        return counters, stats
