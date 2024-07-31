"""
    Splits a project Gutenberg document into chapters.

    Tested on James Fenimore Cooper's The Spy from 1821 (PG code 9845)
"""

import sys
from enum import Enum

START_MARKER = 'CHAPTER'
END_MARKER = '*** END OF THE PROJECT GUTENBERG'


class SectionType(Enum):
    FRONT_MATTER = 'FRONT_MATTER'
    CHAPTER = 'CHAPTER'
    BACK_MATTER = 'BACK_MATTER'


class Configuration:
    def __init__(self, target_directory:str, start_marker:str, end_marker:str):
        self.target_directory = target_directory
        self.start_marker = start_marker
        self.end_marker = end_marker

    def get_target_directory(self):
        return self.target_directory

    def get_start_marker(self):
        return self.start_marker

    def get_end_marker(self):
        return self.end_marker


def slurp_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def file_name_generator(target_directory:str, type:SectionType, counter=None):
    if counter is None:
        if type == SectionType.FRONT_MATTER:
            return f'{target_directory}/chapter/frontm.txt'
        elif type == SectionType.CHAPTER:
            raise ValueError('No counter specified for chapter?')
        else:
            assert type == SectionType.BACK_MATTER
            return f'{target_directory}/chapter/backm.txt'
    else:
        if type == SectionType.FRONT_MATTER or type == SectionType.BACK_MATTER:
            raise ValueError('Cannot specify counter for front matter.')
        else:
            return f'{target_directory}/chapter/{counter:03}.txt'


def section_file(file_path:str, config:Configuration):
    lines = slurp_lines(file_path)

    state = SectionType.FRONT_MATTER
    output_file = file_name_generator(config.target_directory, state)
    chapter = 1
    with open(output_file, 'w') as sect_file:
        for i, line in enumerate(lines):
            if line.startswith(config.get_start_marker()):
                sect_file.close()
                state = SectionType.CHAPTER
                output_file = file_name_generator(config.target_directory, state, chapter)
                chapter += 1
                sect_file = open(output_file, 'w')
                sect_file.write(line)
            elif line.startswith(config.get_end_marker()):
                sect_file.close()
                state = SectionType.BACK_MATTER
                output_file = file_name_generator(config.target_directory, state)
                sect_file = open(output_file, 'w')
            else:
                sect_file.write(line)
    return chapter


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'rawData/pg9845.txt'

    config = Configuration('text/novel/spy1821', START_MARKER, END_MARKER)
    print(f'Writing to {config.get_target_directory()}, using {config.get_start_marker()} and {config.get_end_marker()} as markers.')
    chapters = section_file(file_path, config)
    print(f'Total chapters: {chapters}')