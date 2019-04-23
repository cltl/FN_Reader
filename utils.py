import os
import json
from pathlib import Path
import pandas


def load_paths(category):
    """
    load relevant paths for category
    
    :param str category: supported: 'frame-to-frame'
    
    :rtype: dict
    :return: {
        'category' : 'frame-to-frame-relations' |
        'definitions_path' : json path where possible values of category with definitions are stored,
        'bibtex_path' : path to bibtex with relevant references
    }
    """
    accepted_categories = {'frame-to-frame-relations'}
    cur_dir = Path().resolve()

    possible_values_path = os.path.join(cur_dir, 'terminology', f'{category}.json')
    assert os.path.exists(possible_values_path), f'{category} not among accepted categories: {accepted_categories}'

    bibtex_path = os.path.join(cur_dir, 'terminology', 'main.bib')
    assert os.path.exists(bibtex_path), f'cannot find {bibtex_path}'

    paths = {
        'category' : category,
        'definitions_path': possible_values_path,
        'bibtex_path' : bibtex_path
    }

    return paths


def load_definitions_in_df(settings):
    """
    load definitions into dataframe

    :param dict settings: see output from 'load_paths' in this same python file

    :rtype: pandas.core.frame.DataFrame
    :return: df with information about the definition of each category value
    """
    definitions = json.load(open(settings['definitions_path']))

    list_of_lists = []
    headers = [settings['category'], 'Definition', 'Reference']

    for category_value, info in definitions.items():

        reference = '\\citep{%s}' % info['bibtex_key']
        if info['page']:
            reference = '\\citep[p. %s]{%s}' % (info['page'], info['bibtex_key'])

        one_row = [category_value, info['definition'], reference]
        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df

