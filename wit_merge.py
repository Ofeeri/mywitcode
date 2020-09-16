# upload 177
import hashlib
import os
import shutil


from general_functions import (check_for_wit, create_folder, format_time, get_all_path_hashes,
    get_current_commit_id, get_parent_group, get_wit_path, NoWitError, references_ops, update_staging)


def get_branch_id(branch_name):
    refs_path = os.path.join(f'{get_wit_path()}\\references.txt')
    with open(refs_path, 'r') as refs:
        for line in refs.readlines():
            if branch_name == line.split('=')[0]:
                return line.split('=')[1].strip('\n')


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


def get_shared_base(branch_name):
    """gets shared base between branch and head"""
    head = get_current_commit_id()
    branch_id = get_branch_id(branch_name=branch_name)
    head_tree = get_parent_group(commit_id=head)
    branch_tree = get_parent_group(commit_id=branch_id)
    for item in branch_tree:
        if item in head_tree:
            return item


def hash_decoder(h, commit_id):
    """returns path of file based on its hash"""
    path = get_wit_path(commit_id)
    for root, dirs, files in os.walk(path):
        for f in files:
            f_path = os.path.join(root, f)
            with open(f_path, 'rb') as file:
                file_name = f
                to_hash = file.read() + file_name.encode('utf-8')
                file_hash = hashlib.md5(to_hash).hexdigest()
                if h == file_hash:
                    return os.path.join(root, f)
        for d in dirs:
            folder_name = d
            folder_hash = hashlib.md5(folder_name.encode('utf-8')).hexdigest()
            if h == folder_hash:
                return os.path.join(root, d)


def update_new_commit_folder(path_list, new_commit_id):
    """add all merged files into newly created commit folder"""
    new_commit_path = os.path.join(f'{images_path}\\{new_commit_id}')
    dirs_list = []  # makes sure that dirs and files which are in another dir are not copied twice
    for path in path_list:
        if os.path.isdir(path):
            current_dir_objects = os.listdir(path)
            for obj in current_dir_objects:
                dirs_list.append(obj)
    for path in path_list:
        if os.path.isdir(path) and os.path.basename(path) not in dirs_list:
            destination = f'{new_commit_path}\\{os.path.basename(path)}'
            try:
                shutil.copytree(src=path, dst=destination)
            except FileExistsError:
                shutil.rmtree(destination)
                shutil.copytree(src=path, dst=destination)
        if os.path.isfile(path) and os.path.basename(path) not in dirs_list:
            shutil.copy(path, new_commit_path)


def create_merged_metadata_file(message, folder_name, branch_id):
    """creates text file that stores info about corresponding new folder, and is unique to merge because
        it adds both parents"""
    meta_path = os.path.join(f'''{images_path}\\{folder_name}.txt''')
    with open(meta_path, 'w+') as meta_txt:
        if len(os.listdir(images_path)) == 2:  # this means that only one commit has been called
            meta_txt.write('parent=None\n\n')
        else:
            meta_txt.write(f'parents={get_current_commit_id()},{branch_id}\n\n')
        meta_txt.write(f'date={format_time()}\n\n')
        meta_txt.write(f'message={message}')


def get_different_files(branch):
    """get files which differ between branch and shared base with head"""
    new_paths = []
    base = get_shared_base(branch_name=branch)
    base_path = get_wit_path(keyword=base)
    hashed_base_files = get_all_path_hashes(path=base_path)
    branch_id = get_branch_id(branch_name=branch)
    branch_path = get_wit_path(keyword=branch_id)
    hashed_branch_files = get_all_path_hashes(path=branch_path)
    for h in hashed_branch_files:
        if h not in hashed_base_files:
            new_path = hash_decoder(h=h, commit_id=branch_id)
            new_paths.append(new_path)
    for h in hashed_base_files:
        if h in hashed_branch_files:
            new_path = hash_decoder(h=h, commit_id=branch_id)
            new_paths.append(new_path)
    return new_paths


def merge(branch_name):
    if not check_for_wit():
        raise NoWitError
    new_paths = get_different_files(branch=branch_name)
    if len(new_paths) > 0:
        new_folder = create_folder()
        branch_id = get_branch_id(branch_name=branch_name)
        create_merged_metadata_file(message='merged file', folder_name=new_folder, branch_id=branch_id)
        references_ops(folder_name=new_folder)
        update_new_commit_folder(path_list=new_paths, new_commit_id=new_folder)
        update_staging(commit_id=new_folder)


if check_for_wit():
    staging_path = get_wit_path(keyword='staging_area')
    images_path = get_wit_path(keyword='images')
