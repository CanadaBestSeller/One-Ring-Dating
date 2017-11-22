#!/usr/bin/env python3

from os.path import exists


class FileUtils:

    @staticmethod
    def parse_lines(filepath):
        if not exists(filepath):
            return []
        with open(filepath) as file:
            lines = file.readlines()
            return [line.strip() for line in lines]

    @staticmethod
    def add_line_to_file(filepath, entry):
        with open(filepath, 'a+') as file:
            file.write(entry)
            file.write('\r\n')
