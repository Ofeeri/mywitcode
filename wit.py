# upload 170
import os
import sys

import wit_add
import wit_commit
import wit_checkout
import wit_merge
import wit_status
import wit_graph
import wit_branch


class NoWitError(Exception):
    pass


def check_for_wit():
    for _, dirs, _ in os.walk(os.getcwd()):
        for d in dirs:
            if d == '.wit':
                return True
    return False


def init():
    dir1 = os.path.join(f'{os.getcwd()}\\.wit')
    if os.path.exists(dir1):
        return True
    else:
        os.mkdir(dir1)
        images_dir = os.path.join(f'{dir1}\\images')
        staging_dir = os.path.join(f'{dir1}\\staging_area')
        activated_path = os.path.join(f'{dir1}\\activated.txt')
        os.mkdir(images_dir)
        os.mkdir(staging_dir)
        with open(activated_path, 'w+') as active:
            active.write('Master')


def check_input():  # input in cmd is string that is appended to sys.argv, thus this function is necessary
    action = None
    if sys.argv[1] == 'init':
        action = init()
    if 'add' in sys.argv and sys.argv[1] == 'add':
        path = sys.argv[2]
        action = add(filename=path)
    if 'commit' in sys.argv and sys.argv[1] == 'commit':
        message = None
        if len(sys.argv) == 3:
            message = sys.argv[2]
        action = commit(message=message)
    if 'status' in sys.argv and sys.argv[1] == 'status':
        action = status()
    if 'checkout' in sys.argv and sys.argv[1] == 'checkout':
        if len(sys.argv) == 3:
            commit_id = sys.argv[2]
        action = checkout(commit_id)
    if 'graph' in sys.argv and sys.argv[1] == 'graph':
        action = graph()
    if 'branch' in sys.argv and sys.argv[1] == 'branch':
        branch_name = sys.argv[2]
        action = branch(branch_name=branch_name)
    if 'merge' in sys.argv and sys.argv[1] == 'merge':
        branch_name = sys.argv[2]
        action = merge(branch_name=branch_name)
    return action


add = wit_add.add
commit = wit_commit.commit
status = wit_status.status
checkout = wit_checkout.checkout
graph = wit_graph.graph
branch = wit_branch.branch
merge = wit_merge.merge


check_input()
