from collections import deque
from typing import Final
import key
import yaml

with open('resources/config.yml') as f:
    conf = yaml.safe_load(f)


def parse_daily_text(daily_text: [], data):
    # remember the current line of input string
    line_tracker: int = 0

    # current processing date
    current_date: int = 0

    # to control the initialization of the data list
    is_initialized: bool = False

    # remember whether the previous line was blank line or not
    prev_line_was_blank: bool = False

    #####################
    # parse for each line
    for line in daily_text:
        line_tracker += 1

        line = line.split()  # split by whitespace, continuous whitespace is treated as one

        # check if current line is valid
        __check_validation_of_line(line, len(daily_text), line_tracker, current_date, prev_line_was_blank)

        # blank line
        if len(line) == 0:
            prev_line_was_blank = True
            if current_date == 1:  # if last processed date was 1, then end the loop
                break
        else:
            prev_line_was_blank = False

        # date line
        if __is_date_line(line):
            current_date = int(line[0])

            if is_initialized is False:  # run only once
                # initialize data lists, as size equals to the last day of month
                for i in range(1, int(line[0]) + 1):
                    data.key_data[i] = dict()
                    data.key_orig_texts[i] = dict()
                    data.memo_data[i] = []
                is_initialized = True

        # keyword line
        elif __is_keyword_line(line):
            __parse_keyword_line(line, current_date, data.key_data, data.key_orig_texts)

        # memo line
        elif len(line) > 0:
            data.memo_data[current_date].append(line)


def __check_validation_of_line(line: [], num_of_all_line: int, line_tracker: int
                               , current_date: int, prev_line_was_blank: bool):
    if prev_line_was_blank is True and __is_date_line(line) is False:
        raise print_error_log(line, line_tracker, current_date)  # TODO: line after blank line should be date line
    elif line_tracker == num_of_all_line and current_date != 1:
        raise print_error_log(line, line_tracker, current_date)  # TODO: reached EOF but processed date is not 1
    elif __is_date_line(line) is True and current_date != 0 and int(line[0]) != current_date - 1:
        raise print_error_log(line, line_tracker, current_date)  # TODO: date should be decreasing by 1


def __is_date_line(line: []) -> bool:
    if len(line) == 1 and line[0].isdecimal():
        return True
    else:
        return False


def __is_keyword_line(line: []) -> bool:
    if len(line) > 1 and line[0] in key.KEYWORDS and __is_number(line[1]):
        return True
    else:
        return False


def __parse_keyword_line(line: [], current_date: int, key_data: [], key_orig_texts: []):
    # digit modifier for current currency
    base_digit: Final = conf['base_digit']

    keyword = line.pop(0)
    sum_num = 0

    for word in line:
        if __is_number(word):
            sum_num += float(word)

    if keyword not in key.INT_KEYWORDS:
        sum_num /= 10 ** (base_digit - 1)  # divide sum by base digit

    # since same keyword lines can exist in the same date
    if not key_data[current_date].get(keyword):
        key_data[current_date][keyword] = sum_num
        key_orig_texts[current_date][keyword] = line.copy()
    else:
        key_data[current_date][keyword] += sum_num
        key_orig_texts[current_date][keyword].append("||")
        key_orig_texts[current_date][keyword].extend(line)


# check if it is number (including negative number and float type)
def __is_number(s: str) -> bool:
    return s.lstrip('-').replace('.', '', 1).isdigit()


# TODO: separate it to error handling py file
# print processing data when error occurred
def print_error_log(line: [], line_tracker: int, current_date: int):
    print("processing line: " + str(line_tracker))
    print("processing date: " + str(current_date))
    print("processing line data: " + ' '.join(line))
