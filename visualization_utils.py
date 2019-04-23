import pandas
import seaborn as sns
import matplotlib.pyplot as plt
from graphviz import Graph
import itertools

def plot_num_lu_class2freq(num_lu_class2freq):
    """
    plot num_lu_class2freq
    
    :param dict num_lu_class2freq: num_lu_class -> freq
    
    :rtype:
    """
    list_of_lists = []
    headers = ['LU freq class', 'frequency']

    for lu_class, freq in sorted(num_lu_class2freq.items()):
        list_of_lists.append([lu_class, freq])

    stats = pandas.DataFrame(list_of_lists, columns=headers)

    plt.title('Number of frames with x amount of LUs linked to it')
    plot = sns.lineplot(x='LU freq class', y='frequency', data=stats)
    
    return plot


def plot_fe_relations_of_frame(frame):
    """
    """
    g = Graph('frame', filename='dotgraphs/frame.gv')

    for fe, info in frame.FE.items():

        # add fe as node
        g.node(fe)

        # add excludes relation
        if info.excludesFE is not None:
            g.edge(fe, info.excludesFE.name, label='excludes')

        if info.requiresFE is not None:
            g.edge(fe, info.requiresFE.name, label='requires')


    # add coresets
    if frame.FEcoreSets:
        for index, coreset in enumerate(frame.FEcoreSets):
            label = f'cluster coreset {index}'
            with g.subgraph(name=label) as c:
                names = [coreset_member.name
                         for coreset_member in coreset]
                edges = []
                for node, other_node in itertools.combinations(names, 2):
                    edges.append((node, other_node))
                c.edges(edges)

                c.attr(label=label)
                
    return g