import os
import nltk
from nltk.corpus.reader.framenet import FramenetCorpusReader
from nltk.corpus import framenet as fn17
import networkx as nx
import pandas
from collections import Counter, defaultdict
from datetime import datetime


def load_framenet(version='1.7'):
    """
    load framenet version
    
    :param str version: supported: '1.5' | '1.7'
    
    :rtype: nltk.corpus.reader.framenet.FramenetCorpusReader
    :return: instance of nltk.corpus.reader.framenet.FramenetCorpusReader
    (either version 1.5 or 1.7 of English FrameNet)
    """
    assert version in {'1.5', '1.7'}, f'version {version} not supported, only versions 1.5 and 1.7'

    if version == '1.7':
        fn_instance = fn17
    elif version == '1.5':
        fn_path = os.path.join(nltk.data.path[0], 'corpora', 'framenet_v15')
        fn_instance = FramenetCorpusReader(fn_path, ['frRelation.xml',
                                                     'frameIndex.xml',
                                                     'fulltextIndex.xml',
                                                     'luIndex.xml',
                                                     'semTypes.xml'])

    return fn_instance


fn = load_framenet()
assert len(fn.frames()) == 1221
fn = load_framenet(version='1.7')
assert len(fn.frames()) == 1221
fn = load_framenet(version='1.5')
assert len(fn.frames()) == 1019


def get_dfs_frame_lu_name_relation(fn_instance):
    """
    get two dataframes

    dataframe 1:
    1. LU name, e.g., lemma and pos combination
    2. list of frame IDS that the LU name can evoke

    dataframe 2:
    1. frame ID
    2. list of LU IDs that can evoke the frame

    :param nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instance of
    nltk.corpus.reader.framenet.FramenetCorpusReader

    :rtype: tuple
    :return: (dataframe 1, dataframe 2)
    """
    frame_ids2lu_ids = dict()
    lu_name2frame_ids = dict()

    for lu in fn_instance.lus():
        lu_name2frame_ids[lu.name] = []

    for frame in fn_instance.frames():
        frame_id = frame.ID

        if frame_id not in frame_ids2lu_ids:
            frame_ids2lu_ids[frame_id] = []

        for lu, info in frame.lexUnit.items():

            # lu -> frames
            lu_name2frame_ids[info.name].append(frame_id)

            # frame -> lus
            frame_ids2lu_ids[frame_id].append(info.name)


    dfs = []
    for a_dict, headers in [(frame_ids2lu_ids, ['Frame ID', 'LU IDs', 'Freq']),
                            (lu_name2frame_ids, ['LU ID', 'Frame IDs', 'Freq'])]:

        list_of_lists = []
        for key, value in a_dict.items():
            one_row = [key, value, len(value)]
            list_of_lists.append(one_row)
        df = pandas.DataFrame(list_of_lists, columns=headers)
        dfs.append(df)

    return dfs


def load_frame_relations_as_directed_graph(fn_instance, subset_of_relations=set()):
    """

    :param instance of nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instace of fn version
    :param set subset_of_relations: if empty, all relations are considered
    if not empty, only that subset is considered
    
    possible relations are:
    {'Using', 
    'Subframe', 
    'Metaphor', 
    'Causative_of', 
    'Perspective_on', 
    'Precedes', 
    'See_also', 
    'Inheritance', 
    'Inchoative_of', 
    'ReFraming_Mapping'
    }

    :rtype: networkx.classes.digraph.DiGraph
    :return: directed graph containing all FrameNet frame-to-frame relations
    """
    G = nx.DiGraph()

    relations_set = set()
    
    edges = []
    for frame_relation in fn_instance.frame_relations():
        
        rel_type = frame_relation['type'].name
        if subset_of_relations:
            if rel_type not in subset_of_relations:
                continue

        edge_id = frame_relation.ID
        super_node = f'{frame_relation.superFrameName}'
        sub_node = f'{frame_relation.subFrameName}'
        edges.append((super_node, sub_node, {rel_type : edge_id}))
        
        relations_set.add(rel_type)

    G.add_edges_from(edges)

    return G

def get_all_successors_of_all_successors(graph, starting_node, verbose=0):
    """
    given a directed graph, return all
    successors of all successors, i.e., all nodes below the starting node
    
    :param networkx.classes.digraph.DiGraph graph: directed graph
    :param starting_node: id of starting node
    
    :rtype: dict
    :return: key are the 'depth' (1 being the successors of the starting node)
    {depth -> nodes at that level}
    """
    level2successors = defaultdict(set)
    level = 1

    try:
        current_successors = set(graph.successors(starting_node))
    except nx.NetworkXError:
        if verbose >= 2:
            print(starting_node, 'not found in graph')
        return {0 : {starting_node}}

    while current_successors:

        # update dict 
        level2successors[level] = current_successors

        # successors one leven down
        all_future_successors = set()

        for current_successor in current_successors:
            future_successors = graph.successors(current_successor)
            all_future_successors.update(set(future_successors))

        level += 1
        current_successors = all_future_successors
    
    return level2successors


def df_frame2num_of_fe_types(fn_instance):
    """
    create a df in which each row contains the number of types of FEs per frame,
    e.g., how many of type 'Core', 'Core-Unexpressed', 'Extra-Thematic', 'Peripheral'

    :param instance of nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instace of fn version

    :rtype: pandas.core.frame.DataFrame
    :return: df with FE type information per frame
    """
    core_types = ['Core', 'Core-Unexpressed', 'Extra-Thematic', 'Peripheral']

    headers = ['Frame ID', 'total # of FEs', '# of Core', '# of Core-Unexpressed', '# of Extra-Thematic',
               '# of Peripheral']
    list_of_lists = []

    for frame in fn_instance.frames():

        counts = {core_type: 0 for core_type in core_types}
        actual_counts = Counter([info.coreType for fe, info in frame.FE.items()])
        counts.update(actual_counts)

        one_row = [frame.ID]
        one_row.append(sum(counts.values()))
        for core_type in core_types:
            one_row.append(counts[core_type])

        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df



def df_fe2num_frames(fn_instance):
    """
    create a df in which each row contains the number of frames that a FE is a part of

    :param instance of nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instace of fn version


    :rtype: pandas.core.frame.DataFrame
    :return: df with for each FE the number of frames it is part of

    :param fn_instance:
    :return:
    """
    fe2frame_ids = defaultdict(set)

    for frame in fn_instance.frames():
        frame_id = frame.ID
        for fe, info in frame.FE.items():
            fe2frame_ids[fe].add(frame_id)

    headers = ['FE', 'Frame IDs', '# of Frame IDs']
    list_of_lists = []
    for fe, frame_ids in fe2frame_ids.items():
        list_of_lists.append((fe, frame_ids, len(frame_ids)))

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df


def df_fe2coreness_types(fn_instance):
    """
    create a df in which each row contains for an FE
    1. how many times as core
    2. how many times as peripheral
    3. how many times as core-unexpressed
    4. how many times as extra-thematic

    :param instance of nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instace of fn version


    :rtype: pandas.core.frame.DataFrame
    :return: df with for each FE the frequency per coreness type
    """
    fe2frame_ids = defaultdict(set)

    for frame in fn_instance.frames():
        frame_id = frame.ID
        for fe, info in frame.FE.items():
            fe2frame_ids[fe].add(frame_id)


    #headers = ['FE', 'Frame IDs', '# of Frame IDs']
    #list_of_lists = []
    #for fe, frame_ids in fe2frame_ids.items():
    #    list_of_lists.append((fe, frame_ids, len(frame_ids)))

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df


def get_gf_and_pos2annotations(fn_instance, verbose=0):
    """


    :param instance of nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instace of fn version

    :rtype: collections.defaultdict
    :return: mapping of (POS, GF) -> annotations
    """
    pos_and_gf2annotations = defaultdict(list)
    set_pos = set()
    set_gf = set()
    for annotation in fn_instance.annotations(full_text=False):
        pos = annotation.LU.POS
        for start, end, gf in annotation.GF:
            key = (pos, gf)
            pos_and_gf2annotations[key].append(annotation)

            set_pos.add(pos)
            set_gf.add(gf)

    if verbose:
        print('parts of speech', set_pos)
        print('grammatical functions', set_gf)


    return pos_and_gf2annotations



def get_pt_and_pos2annotations(fn_instance, verbose=0):
    """


    :param instance of nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: instace of fn version

    :rtype: collections.defaultdict
    :return: mapping of (POS, PT) -> annotations
    """
    pos_and_pt2annotations = defaultdict(list)
    set_pos = set()
    set_pt = set()
    for index, annotation in enumerate(fn_instance.annotations(full_text=False, exemplars=True)):
        pos = annotation.LU.POS

        if verbose >= 2:
            if index % 10000 == 0:
                print(index, datetime.now())

        for start, end, pt in annotation.PT:
            key = (pos, pt)

            if len(pos_and_pt2annotations[key]) <= 1000:
                pos_and_pt2annotations[key].append(annotation)

            set_pos.add(pos)
            set_pt.add(pt)

    if verbose:
        print('parts of speech', set_pos)
        print('phrase types', set_pt)


    return pos_and_pt2annotations