from shutil import rmtree
import os
from collections import defaultdict
from collections import Counter
import json


def get_lu(lu, pos_in_lu=False, pos_mapping=dict()):
    lemma, pos = lu.rsplit('.')

    if pos_mapping:
        pos = pos_mapping[pos]

    if pos_in_lu:
        lu_to_use = (lemma, pos)
    else:
        lu_to_use = lemma

    return lu_to_use



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

            lu_to_use = get_lu(lu, pos_in_lu=pos_in_lu, pos_mapping=pos_mapping)

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
        frame_label = frame.name
        roles = []

        for fe, role_info in frame.FE.items():

            role_id = str(role_info.ID)
            role_definition = role_info.definition
            role_label = role_info.name
            role_type = role_info.coreType

            role_info = {
                'role_id' : role_id,
                'role_label' : role_label,
                'role_definition' : role_definition,
                'role_type' : role_type
            }

            roles.append(role_info)

        info = {
            'definition' : definition,
            'frame_label' : frame_label,
            'roles' : roles,
        }

        frame_to_info[frame.ID] = info

    if verbose:
        print()
        print(f'found {len(frame_to_info)} frames')

    return frame_to_info


def get_dominant_frame_info(fn_instance,
                            event_type_to_dominant_frame,
                            pos_in_lu=False,
                            pos_mapping=dict(),
                            ):
    """
    load event_type_to_dominant_frame and add for each event_type:
    'lu_to_dominant_frame' -> mapping from lu to dominant frame


    :param nltk.corpus.reader.framenet.FramenetCorpusReader fn_instance: loaded instance of FrameNet in nltk
    :param dict event_type_to_dominant_frame: mapping of event_type -> dominant_frame information
    (see fn_tool_input/event_type_to_dominant_frame.json for example)
    :return:
    """


    for event_type, info in event_type_to_dominant_frame.items():

        event_type_to_dominant_frame[event_type]['lu_to_dominant_frame'] = {}
        lu_to_frames = defaultdict(set)

        for label_key, id_key in [('main_frame_labels', 'main_frame_ids'),
                                  ('subframe_labels', 'subframe_ids')]:

            frame_labels = info[label_key]
            info[id_key] = []
            for frame_label in frame_labels:

                frame = fn_instance.frame_by_name(frame_label)
                frame_id = frame.ID

                info[id_key].append(frame_id)

                for lu, lu_info in frame.lexUnit.items():
                    lu_to_use = get_lu(lu, pos_in_lu=pos_in_lu, pos_mapping=pos_mapping)
                    lu_to_frames[lu_to_use].add(frame_id)

                for lu, frames in lu_to_frames.items():
                    if len(frames) == 1:
                        event_type_to_dominant_frame[event_type]['lu_to_dominant_frame'][lu] = frames.pop()


    return event_type_to_dominant_frame








def create_tool_input(output_folder,
                      fn_instance,
                      readme_path,
                      event_type_to_dominant_frame_path,
                      pos_in_lu=False,
                      pos_mapping=dict(),
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
                                     pos_mapping=pos_mapping,
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

        if verbose >= 1:
            print()
            print(f'written frame info to {frame_path}')

    event_type_to_dominant_frame = json.load(open(event_type_to_dominant_frame_path))

    dominant_frame_info = get_dominant_frame_info(fn_instance=fn,
                                                  event_type_to_dominant_frame=event_type_to_dominant_frame,
                                                  pos_in_lu=pos_in_lu,
                                                  pos_mapping=pos_mapping)

    dominant_frame_info_path = os.path.join(output_folder, 'event_type_to_dominant_frame.json')

    with open(dominant_frame_info_path, 'w') as outfile:
        json.dump(dominant_frame_info, outfile, indent=4, sort_keys=True)

        if verbose >= 1:
            print()
            print(f'written dominant frame info to {dominant_frame_info_path}')


if __name__ == '__main__':
    import json
    from stats_utils import load_framenet

    fn = load_framenet(version='1.7')
    verbose = 2

    create_tool_input(output_folder='fn_tool_information',
                      readme_path='FrameNet input to tool.md',
                      event_type_to_dominant_frame_path='fn_tool_input/event_type_to_dominant_frame.json',
                      fn_instance=fn,
                      verbose=verbose)



