# upload 174
import os
import shutil

from general_functions import check_for_wit, get_files_not_staged, get_files_to_be_committed, get_wit_path, NoWitError


def copy_committed_files(commit_path):
    """this function copies all files and dirs in commit_path, in case of dir deletes dir in cwd and replaces it with
        updated one. Try and except deals with case in which the function tries to copy a file thas is within a
        directory (this will be handled by copying whole directory). os.listdir check makes sure that only top
        directories in commit_path are copied"""
    for _, dirs, files in os.walk(commit_path):
        for f in files:
            source = os.path.join(f'{commit_path}\\{f}')
            destination = os.getcwd()
            try:
                shutil.copy(src=source, dst=destination)
            except FileNotFoundError:
                pass
        for d in dirs:
            if d in os.listdir(commit_path):
                source = os.path.join(f'{commit_path}\\{d}')
                destination = os.path.join(f'{os.getcwd()}\\{d}')
                try:
                    shutil.copytree(src=source, dst=destination)
                except FileExistsError:
                    shutil.rmtree(destination)
                    shutil.copytree(src=source, dst=destination)


def update_staging(commit_id):
    """copies contents of images\\commit_id into staging area"""
    source = os.path.join(f'{images_path}\\{commit_id}')
    dest = os.path.join(f'{staging_path}')
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src=source, dst=dest)


def update_references(commit_id):
    with open(refs_path, 'r+') as refs:
        lines = refs.readlines()
        lines[0] = f'Head={commit_id}\n'
    with open(refs_path, 'w') as refs:
        for line in lines:
            refs.write(line)


def get_master_id():
    with open(refs_path, 'r') as refs:
        master_id = refs.readlines()[1].strip('\n')[7:]
    return master_id.strip()


def update_activated(input_id):
    activated_path = os.path.join(f'{get_wit_path()}\\activated.txt')
    new_active = ''
    with open(refs_path, 'r') as refs:
        lines = refs.readlines()
        for line in lines:
            if line.split('=')[0] == input_id:
                new_active = input_id
    with open(activated_path, 'w') as active:
        active.write(new_active)


def check_if_branch(input_id):
    with open(refs_path, 'r') as refs:
        branches = refs.readlines()[1:]
        for branch in branches:
            if branch.split('=')[0] == input_id:
                return True
    return False


def get_branch_id(input_id):
    with open(refs_path, 'r') as refs:
        branches = refs.readlines()[1:]
        for branch in branches:
            if branch.split('=')[0] == input_id:
                branch_id = branch.split('=')[1].strip('\n')
                return branch_id


def checkout(input_id):
    if not check_for_wit():
        raise NoWitError(f'No .wit folder exists in {os.getcwd()}')
    if len(get_files_not_staged()) > 0:
        print(f'There are files which have been changed in {os.getcwd()} since added to staging area, checkout not executed')
        return False
    if len(get_files_to_be_committed()) > 0:
        print('There are files which have been added to or changed in staging area since last commit, checkout not executed')
        return False
    commit_id = input_id
    if check_if_branch(input_id=input_id):
        commit_id = get_branch_id(input_id=input_id)
    commit_id_path = get_wit_path(keyword=commit_id)
    copy_committed_files(commit_path=commit_id_path)
    update_staging(commit_id=commit_id)
    update_activated(input_id)
    update_references(commit_id=commit_id)


if check_for_wit():
    images_path = get_wit_path(keyword='images')
    staging_path = get_wit_path(keyword='staging_area')
    wit_path = get_wit_path()
    refs_path = os.path.join(f'{get_wit_path()}\\references.txt')
