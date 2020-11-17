import unittest

from src.analysis import DigitCounterAnalysis, WrongFile, WrongLetter, WrongColumn


class TestAnalysis(unittest.TestCase):
    def setUp(self) -> None:
        self.filename = 'simple_data.tsv'
        self.wrong_filename = 'wrong_file'

    def test_read(self):
        DigitCounterAnalysis(self.filename)

    def test_wrong_file(self):
        with self.assertRaises(WrongFile):
            DigitCounterAnalysis(self.wrong_filename)

    def test_counting_whole(self):
        right_answers = {'0': 7, '1': 4, '2': 3, '3': 9, '4': 6, '5': 0, '6': 0, '7': 5, '8': 8, '9': 7}
        analysis = DigitCounterAnalysis(self.filename)
        for digit in right_answers:
            answer = analysis.get_count(digit)
            right_answer = right_answers[digit]
            self.assertEqual(answer, right_answer)

    def test_counting_column(self):
        right_answers = {'0': 2, '1': 0, '2': 2, '3': 1, '4': 1, '5': 0, '6': 0, '7': 2, '8': 1, '9': 2}
        column = '7_2009'
        analysis = DigitCounterAnalysis(self.filename)
        for digit in right_answers:
            answer = analysis.get_count(digit, column)
            right_answer = right_answers[digit]
            self.assertEqual(answer, right_answer)

    def test_wrong_column(self):
        analysis = DigitCounterAnalysis(self.filename)
        with self.assertRaises(WrongColumn):
            analysis.get_count('0', 'wrong_column')

    def test_wrong_letter(self):
        analysis = DigitCounterAnalysis(self.filename)
        with self.assertRaises(WrongLetter):
            analysis.get_count('a')

    def test_counting_column_as_int(self):
        right_answers = {'0': 2, '1': 0, '2': 2, '3': 1, '4': 1, '5': 0, '6': 0, '7': 2, '8': 1, '9': 2}
        column = '7_2009'
        analysis = DigitCounterAnalysis(self.filename)
        for digit in right_answers:
            i_digit = int(digit)
            answer = analysis.get_count(i_digit, column)
            right_answer = right_answers[digit]
            self.assertEqual(answer, right_answer)


if __name__ == '__main__':
    unittest.main()
