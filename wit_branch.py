# upload 176
import os

from general_functions import check_for_wit, get_current_commit_id, get_wit_path, NoWitError


def update_branch_reference(branch_name):
    refs_path = os.path.join(f'{get_wit_path()}\\references.txt')
    with open(refs_path, 'a') as refs:
        refs.write(f'{branch_name}={get_current_commit_id()}\n')


def branch(branch_name):
    if not check_for_wit():
        raise NoWitError
    else:
        update_branch_reference(branch_name=branch_name)
