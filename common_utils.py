"""
    Functions that ended up being useful in other scripts.
"""

from enum import Enum

class SectionType(Enum):
    FRONT_MATTER = 'FRONT_MATTER'
    CHAPTER = 'CHAPTER'
    BACK_MATTER = 'BACK_MATTER'


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

