from collections import Counter
from hashlib import sha256
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


class WrongCountersType(Exception):
    """Exception raised when trying to get counters of wrong type than allowed."""

    def __init__(self, c_type: str):
        self.message = f'Wrong counter type = {c_type}'
        super().__init__(self.message)


class Reader:
    """Class for reading from file.

    Args:
        filename (str): path to file to analyze, stored locally
        ext (str): file format, if empty, try recognizing
            by extension
    """

    supported_extensions = {
        '.tsv': '\t',
        '.csv': ',',
    }

    def __init__(self, filename: str, ext: str = ''):
        self.file = Path(filename)
        if not self.file.exists():
            raise WrongFile(filename, 'not-exists')

        # if ext properly provided, use read_csv function
        if ext in Reader.supported_extensions:
            self.ext = ext
        # if mode not provided, try to recognize file by extension
        else:
            if (ext := self.file.suffix.lower()) in Reader.supported_extensions:
                self.ext = ext
            else:
                self.ext = ''  # extension should be empty if not recognized

        self.delim = Reader.supported_extensions.get(self.ext, ',')

        # add extension which were used to parse to id for making distinctions
        self.id = Reader.file_id(self.file, self.ext)

    def __iter__(self):
        """Iterating over lines in file.

        Returns:
            next line yielded from file
        """
        yield from self.read_csv(self.file)

    def read_csv(self, file: Path):
        import csv
        with file.open('r', newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=self.delim)
            yield from reader

    @staticmethod
    def file_id(file: Path, ext: str) -> str:
        """Unique file ID per content, filename not included except extension."""
        # add extension which were used to parse to id for making distinctions
        return f'{Reader.sha256sum(file)}{ext}'

    @staticmethod
    def same_files(file1: Path, file2_content):
        """Check if content of"""
        return Reader.sha256sum(file1) == Reader.sha256sum_b(file2_content)

    @staticmethod
    def sha256sum(file: Path) -> str:
        with file.open('rb') as opened_file:
            return Reader.sha256sum_b(opened_file)

    @staticmethod
    def sha256sum_b(f_stream) -> str:
        sha256_hash = sha256()
        for byte_block in iter(lambda: f_stream.read(4096), b''):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def get_supported_extensions():
        return list(Reader.supported_extensions.keys())


class DigitCounterAnalysis:
    """Class for reading file with data and analyze digits distributions.
    If possible, digits distributions will be available to analyze per column in data.

    Args:
        filename (str): path to file to analyze, stored locally
        ext (str): file format

    Attributes:
        filename (str): path to file to analyze, stored locally
    """

    def __init__(self, filename: str, /, *, ext: str = ''):
        counters, lead_counters, stats = DigitCounterAnalysis.analyze_file(filename, ext)
        self._stats = stats
        # set analysis id as file hash
        self.id = stats['hash']

        def to_digit_counters(sel_counters):
            """Convert counters to digit only counters"""
            return {
                column: DigitCounterAnalysis.to_digit_counter(counter)
                for column, counter in sel_counters.items()
            }

        # simple counters
        self._digit_counters = to_digit_counters(counters)
        self._digit_lead_counters = to_digit_counters(lead_counters)

        # counters converted to frequenters
        self._digit_frequenters = DigitCounterAnalysis.to_frequenters(self._digit_counters)
        self._digit_lead_frequenters = DigitCounterAnalysis.to_frequenters(self._digit_lead_counters)

        # merge all counters for whole file analysis and add counter from header which was not included
        self._merged_digit_counter = DigitCounterAnalysis.get_merged_digit_counter(self._digit_counters)
        self._merged_digit_lead_counter = DigitCounterAnalysis.get_merged_digit_counter(self._digit_lead_counters)

        self._stats['benford'] = {
            column: DigitCounterAnalysis.benfords_law(frequenter)
            for column, frequenter in self._digit_lead_frequenters.items()
        }

    def get_stats(self) -> Dict[str, Union[str, int]]:
        return self._stats

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

    def get_counters(self, c_type: str) -> Dict[str, Counter]:
        """Get all counters per column, counter types = ['lead', 'simple']"""
        if c_type == 'simple':
            return self._digit_counters
        elif c_type == 'lead':
            return self._digit_lead_counters
        else:
            raise WrongCountersType

    def get_frequenters(self, c_type: str) -> Dict[str, Dict[str, float]]:
        """Get all frequenters per column, counter types = ['lead', 'simple']"""
        if c_type == 'simple':
            return self._digit_frequenters
        elif c_type == 'lead':
            return self._digit_lead_frequenters
        else:
            raise WrongCountersType

    @staticmethod
    def benfords_law(frequenter: Dict[str, float]):
        """Use Two-sample Kolmogorov-Smirnov test to calculate p-values for Benford's law

        Performing Two-sample Kolmogorov-Smirnov test on predefined Benford's law
        digits distribution with frequenter from data.

        Args:
            frequenter (Dict[str, float]): frequenter as dict where digits (as strings)
                are keys, and their frequencies as values

        """
        from scipy.stats import ks_2samp

        # benford's law digits distribution
        bl_frequencies = {
            '1': 30.1,
            '2': 17.6,
            '3': 12.5,
            '4': 9.7,
            '5': 7.9,
            '6': 6.7,
            '7': 5.8,
            '8': 5.1,
            '9': 4.6,
        }
        bl_f = []
        sa_f = []
        for digit in bl_frequencies:
            bl_f.append(bl_frequencies[digit])
            sa_f.append(frequenter[digit])
        result = ks_2samp(bl_f, sa_f)

        return round(result.pvalue, 4)

    @staticmethod
    def to_frequenters(digit_counter: Dict[str, Counter]) -> Dict[str, Dict[str, float]]:
        """Convert counter to frequenters, care about dividing by 0"""
        f_counters = {
            column: {
                letter:
                    round((counter[letter] * 100.0) / c_sum, 1)
                    if (c_sum := sum(counter.values())) > 0
                    else 0
                for letter in counter
            }
            for column, counter in digit_counter.items()
        }
        return f_counters

    @staticmethod
    def get_merged_digit_counter(counters: Dict[str, Counter]) -> Counter:
        """Merge all counters"""
        # merge all counters from dict
        merged_counter = sum(counters.values(), Counter())

        # need to add counter for header line
        header_counter = Counter(''.join(counters.keys()))

        # needs to again convert to digit counter
        merged_counter = DigitCounterAnalysis.to_digit_counter(merged_counter + header_counter)

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
            2nd: dictionary of lead counters, where keys are columns names
                and values are counters for leading letters in those columns
            3rd: dictionary with statistics from parsing file
        """

        reader = Reader(filename, ext)
        reader_it = iter(reader)

        # get file header
        header = next(reader_it)

        # create counter for each column in header
        header_len = len(header)
        counters = [Counter() for _ in header]
        lead_counters = [Counter() for _ in header]

        # iterate over each line, and each element in line
        # count omitted lines
        omitted_lines = 0
        parsed_lines = 0
        parsed_words = 0
        for line in reader_it:
            parsed_lines += 1
            if len(line) != header_len:
                # we can enforce only proper files
                # but we may also handle this
                # raise WrongFile(filename, 'corrupted')
                omitted_lines += 1
                continue
            for i, elem in enumerate(line):
                parsed_words += 1
                # count leading letters only if len(elem) > 0
                if elem:
                    lead_counters[i] += Counter(elem[0])

                counters[i] += Counter(elem)

        def map_counter(sel_counters, columns):
            """Map counters to columns"""
            return {
                column: counter
                for column, counter in zip(columns, sel_counters)
            }

        counters = map_counter(counters, header)
        lead_counters = map_counter(lead_counters, header)
        stats = {
            'filename': reader.file.name,
            'ext': reader.ext,
            'header_size': header_len,
            'parsed_lines': parsed_lines,
            'omitted_lines': omitted_lines,
            'parsed_words': parsed_words,
            'hash': reader.id,
        }
        return counters, lead_counters, stats
