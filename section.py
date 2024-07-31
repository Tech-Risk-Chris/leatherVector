"""
    Splits a project Gutenberg document into chapters.

    Tested on James Fenimore Cooper's The Spy from 1821 (PG code 9845)
"""
import argparse
import os
from common_utils import SectionType, file_name_generator

START_MARKER = 'CHAPTER'
END_MARKER = '*** END OF THE PROJECT GUTENBERG'


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


def configure_arg_parser():
    parser = argparse.ArgumentParser(description='Section a text file based on chapter and backmatter.')

    parser.add_argument('text_file', type=str,
                        help='The text file to process', default='rawData/pg9845.txt')
    parser.add_argument('target_directory', type=str,
                        help='The directory to split the chapters into', default='text/novel/spy1821')

    parser.add_argument('--chapter', type=str, help='The chapter marker string', default=START_MARKER)
    parser.add_argument('--end', type=str, help='The end-of-ebook string', default=END_MARKER)

    return parser


if __name__ == "__main__":
    args = configure_arg_parser().parse_args()

    os.makedirs(f'{args.target_directory}/chapter', exist_ok=True)

    config = Configuration(args.target_directory, args.chapter, args.end)
    print(f'Writing to {config.get_target_directory()}, using {config.get_start_marker()} and {config.get_end_marker()} as markers.')
    chapters = section_file(args.text_file, config)
    print(f'Total chapters: {chapters}')