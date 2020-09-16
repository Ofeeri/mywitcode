# upload 175
import os

from general_functions import check_for_wit, get_current_commit_id, get_master_id, get_wit_path, NoWitError
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def get_parent(commit_id):
    commit_path = get_wit_path(keyword=commit_id)
    commit_path += '.txt'
    with open(commit_path, 'r') as meta_file:
        parent_line = meta_file.readlines()[0]
        if parent_line.split('=')[0].strip() == 'parent':
            parent = parent_line.split('=')[1].strip()
            return parent
        if parent_line.split('=')[0] == 'parents':
            parents = parent_line.split('=')
            parent1 = parents[1].split(',')[0].strip()
            parent2 = parents[1].split(',')[1].strip('\n')
            return parent1, parent2


def get_parent_group(commit_id):
    """gets list of all parents in a hierarchy from start point (commit_id)"""
    parents_group = []
    parents_tier = [commit_id]
    checked_ids = []
    parents_group.append(commit_id)
    while 'None' not in parents_group:
        for item in parents_tier:
            direct_parent = get_parent(item)
            checked_ids.append(item)
            if direct_parent not in parents_group and type(direct_parent) == str:
                parents_group.append(direct_parent)
            if isinstance(direct_parent, tuple):
                parent1 = direct_parent[0]
                parent2 = direct_parent[1]
                if parent1 not in parents_group:
                    parents_group.append(parent1)
                if parent2 not in parents_group:
                    parents_group.append(parent2)
        for item in parents_group:
            if item not in checked_ids or item not in parents_tier:
                parents_tier.append(item)
            else:
                parents_tier.remove(item)
    parents_group.remove(parents_group[-1])
    return parents_group


def get_from_and_to_list():
    head = get_current_commit_id()
    hierarchy = get_parent_group(commit_id=head)
    from_list = []
    to_list = []
    for item in hierarchy:
        parent = get_parent(item)
        if parent == 'None':
            return from_list, to_list
        if type(parent) == str:
            from_list.append(item)
            to_list.append(parent)
        if type(parent) == tuple:
            from_list.append(item)
            from_list.append(item)
            parent1 = parent[0]
            parent2 = parent[1]
            to_list.append(parent1)
            to_list.append(parent2)


def sort_graph():
    """prepares info in way that it can be graphed correctly"""
    from_list = get_from_and_to_list()[0]
    to_list = get_from_and_to_list()[1]
    head = get_current_commit_id()
    master = get_master_id()
    from_list = [commit_id[:6] for commit_id in from_list]
    to_list = [commit_id[:6] for commit_id in to_list]
    if head == master:
        for index, commit_id in enumerate(from_list):
            if commit_id in head:
                from_list[index] = 'Head and master:\n' + commit_id
    else:
        for commit_id in from_list:
            if commit_id in master:
                index = from_list.index(commit_id)
                from_list[index] = 'Master:\n' + commit_id
            if commit_id in head:
                index = from_list.index(commit_id)
                from_list[index] = 'Head:\n' + commit_id
        for commit_id in to_list:
            if commit_id in master:
                index = to_list.index(commit_id)
                to_list[index] = 'Master:\n' + commit_id
    df = pd.DataFrame({'from': from_list, 'to': to_list})
    G = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph())
    nx.draw(G, with_labels=True, node_size=3800, alpha=1.0, pos=nx.spring_layout(G), arrows=True)
    plt.show()


def graph():
    if not check_for_wit():
        raise NoWitError(f'No .wit folder exists in {os.getcwd()}')
    if len(os.listdir(get_wit_path(keyword='images'))) == 0:
        print('No commits have occurred, there is nothing to be graphed')
        return False
    sort_graph()
