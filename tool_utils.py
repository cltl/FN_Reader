from shutil import rmtree
import os
from collections import defaultdict
from collections import Counter
import json

def load_lu_to_frames(fn_instance,
                      pos_in_lu=False,
                      pos_mapping=dict(),
                      verbose=0):
    """

    :param nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: loaded instance of FrameNet in nltk
    :param bool pos_in_lu: True, keep pos in lu, False, only use lemma

    :rtype: dict
    :return: mapping of lu -> candidate frames
    """
    lu_to_frames = defaultdict(set)

    for frame in fn_instance.frames():
        frame_ID = str(frame.ID)

        for lu, info in frame.lexUnit.items():

            lemma, pos = lu.rsplit('.')

            if pos_mapping:
                pos = pos_mapping[pos]

            if pos_in_lu:
                lu_to_use = (lemma, pos)
            else:
                lu_to_use = lemma

            lu_to_frames[lu_to_use].add(frame_ID)

    for key, value in lu_to_frames.items():
        lu_to_frames[key] = list(value)

    if verbose:
        print()
        print(f'found {len(lu_to_frames)} unique lexical units')
        distribution = [len(value) for value in lu_to_frames.values()]
        print(f'distribution: {Counter(distribution)}')

    return lu_to_frames


def load_frame_to_info(fn_instance, verbose=0):
    """
    load information per frames:
    - definition
    - roles
    - TODO: role relations

    :param nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: loaded instance of FrameNet in nltk
    :return:
    """
    frame_to_info = {}

    for frame in fn_instance.frames():

        definition = frame.definition
        roles = []

        for fe, role_info in frame.FE.items():

            role_id = str(role_info.ID)
            role_definition = role_info.definition
            role_type = role_info.coreType

            role_info = {
                'role_id' : role_id,
                'role_definition' : role_definition,
                'role_type' : role_type
            }

            roles.append(role_info)

        info = {
            'definition' : definition,
            'roles' : roles,
        }

        frame_to_info[frame.ID] = info

    if verbose:
        print()
        print(f'found {len(frame_to_info)} frames')

    return frame_to_info



def create_tool_input(output_folder,
                      fn_instance,
                      readme_path,
                      pos_in_lu=False,
                      verbose=0):
    """

    :param str output_folder: where output is stored.
    if folder exists, it will be removed
    :return:
    """
    if os.path.exists(output_folder):
        rmtree(output_folder)

    os.mkdir(output_folder)

    lu_to_frames = load_lu_to_frames(fn_instance,
                                     pos_in_lu=pos_in_lu,
                                     verbose=verbose)

    lu_path = os.path.join(output_folder, 'lu_to_frames.json')
    with open(lu_path, 'w') as outfile:
        json.dump(lu_to_frames, outfile, indent=4, sort_keys=True)

        if verbose >= 1:
            print()
            print(f'written lu to frame mapping to {lu_path}')

    readme_output_path = os.path.join(output_folder, 'README.md')
    with open(readme_path) as infile:
        with open(readme_output_path, 'w') as outfile:
            outfile.write(infile.read())

        if verbose >= 1:
            print()
            print(f'written README to {readme_output_path}')

    frame_to_info = load_frame_to_info(fn_instance, verbose=verbose)

    frame_path = os.path.join(output_folder, 'frame_to_info.json')
    with open(frame_path, 'w') as outfile:
        json.dump(frame_to_info, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
    from stats_utils import load_framenet

    fn = load_framenet(version='1.7')
    verbose = 2

    create_tool_input(output_folder='fn_tool_information',
                      readme_path='FrameNet input to tool.md',
                      fn_instance=fn,
                      verbose=verbose)


