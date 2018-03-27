# coding=utf-8
import string
import unicodedata


def remove_punctuation(text):
    return text.translate(
        dict((ord(char), None) for char in string.punctuation))


def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if
                   unicodedata.category(c) != 'Mn')
