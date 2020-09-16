# upload 172
import datetime
from datetime import date
import hashlib
import os
import random
import shutil

from general_functions import check_for_wit, NoWitError


def get_wit_path(keyword=None):
    """returns accurate path, keyword can be 'images' or 'staging_area' because
    those are the dirs to be found in .wit. If no keyword is given, return the path of .wit dir"""
    if not keyword:
        keyword = '.wit'
    for root, dirs, _ in os.walk(os.getcwd()):
        for d in dirs:
            if d == keyword and '.wit' in root:
                path = os.path.join(root, d)
                return path
            if d == keyword:
                path = os.path.join(root, d)
                return path


def create_folder():
    """creates new path to be stored in .wit\\images"""
    file_name_chars: str = '1234567890abcdef'
    folder_name: str = ''
    name_length = 40
    while len(folder_name) < name_length:
        folder_name += random.choice(file_name_chars)
    dir1 = os.path.join(f'{images_path}\\{folder_name}')
    os.mkdir(dir1)
    return folder_name


def create_metadata_file(message, folder_name):
    """creates text file that stores info about corresponding new folder """
    meta_path = os.path.join(f'''{images_path}\\{folder_name}.txt''')
    with open(meta_path, 'w+') as meta_txt:
        if len(os.listdir(images_path)) == 2:  # this means that only one commit has been called
            meta_txt.write('parent=None\n\n')
        else:
            meta_txt.write(f'parent={get_current_commit_id()}\n')
        meta_txt.write(f'date={format_time()}\n\n')
        meta_txt.write(f'message={message}')


def format_time():
    """returns time in desired format"""
    now = str(datetime.datetime.now())[:19]
    today = str(date.today().strftime('%A %d %B %Y'))
    return today + now[4:]


def copy_staging(folder_name):
    """copies contents of staging area into new 'image' folder"""
    source = os.path.join(f'{staging_path}')
    dest = os.path.join(f'{images_path}\\{folder_name}')
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src=source, dst=dest)


def references_ops(folder_name):
    """creates or updates references.txt"""
    refs_path = os.path.join(f'{get_wit_path()}\\references.txt')
    if not os.path.exists(refs_path):
        open(refs_path, 'w+')
        with open(refs_path, 'w') as refs:
            refs.write(f'Head={folder_name}\n')
            refs.write(f'Master={folder_name}\n')
    else:
        head = get_current_commit_id()
        master = get_master_id()
        if get_branch_info():
            branch_name = get_branch_info()[0].strip()
            branch_id = get_branch_info()[1].strip()
        else:
            branch_name = None
            branch_id = None
        if head == branch_id:
            with open(refs_path, 'r') as refs:
                lines = refs.readlines()
            with open(refs_path, 'w') as refs:
                refs.write(f'Head={folder_name}\n')
                for branch in lines[1:]:
                    if branch.split('=')[0] == branch_name:
                        refs.write(f'{branch_name}={folder_name}\n')
                    else:
                        refs.write(branch)
        else:
            with open(refs_path, 'r') as refs:
                lines = refs.readlines()
            with open(refs_path, 'w') as refs:
                refs.write(f'Head={folder_name}\n')
                refs.write(f'Master={master}\n')
                for branch in lines[2:]:
                    refs.write(branch)


def get_current_commit_id():
    refs_path = os.path.join(f'''{get_wit_path()}\\references.txt''')
    with open(refs_path, 'r') as refs:
        current_id = refs.readlines()[0].strip('\n')[5:]
    return current_id


def get_master_id():
    refs_path = os.path.join(f'''{get_wit_path()}\\references.txt''')
    with open(refs_path, 'r') as refs:
        master_id = refs.readlines()[1].strip('\n')[7:]
    return master_id


def get_branch_info():
    refs_path = os.path.join(f'{get_wit_path()}\\references.txt')
    with open(refs_path, 'r') as refs:
        lines = refs.readlines()
        for branch in lines[1:]:
            if get_activated() == branch.split('=')[0]:
                branch_name = branch.split('=')[0]
                branch_id = branch.split('=')[1].strip('\n')
                return branch_name, branch_id


def get_activated():
    activated_path = os.path.join(f'{get_wit_path()}\\activated.txt')
    with open(activated_path, 'r') as active:
        branch = active.read()
        return branch


def get_all_path_hashes(path):
    """creates list of hashes of all files in a directory"""
    file_paths = []
    hashes = []
    for root, dirs, files in os.walk(path):
        for f in files:
            new_path = os.path.join(root, f)
            with open(new_path, 'rb') as f:
                file_name = os.path.basename(new_path)
                to_hash = f.read() + file_name.encode('utf-8')
                new_hash = hashlib.md5(to_hash).hexdigest()
                hashes.append(new_hash)
            file_paths.append(new_path)
        for d in dirs:
            new_hash = hashlib.md5(d.encode('utf-8')).hexdigest()
            hashes.append(new_hash)
    return hashes


def check_if_changed():
    """checks if changes have been made to staging area by comparing current hashes of paths in
    staging area against hashes of files currently in head folder in .wit\\images"""
    if not len(os.listdir(images_path)) == 0:
        current_staging_hashes = get_all_path_hashes(staging_path)
        head_path = get_wit_path(keyword=get_current_commit_id())
        head_hashes = get_all_path_hashes(head_path)
    else:
        return True
    changed = False
    if len(current_staging_hashes) != len(head_hashes):
        changed = True
    else:
        for staging_hash in current_staging_hashes:
            if staging_hash not in head_hashes:
                changed = True
    if changed:
        return True
    return False


def commit(message):
    if not check_for_wit():
        raise NoWitError(f'No .wit folder exists in {os.getcwd()}')
    if len(os.listdir(staging_path)) == 0:
        print('Staging area is empty, no files to be committed')
        return False
    if check_if_changed():
        folder_name = create_folder()
        create_metadata_file(message=message, folder_name=folder_name)
        references_ops(folder_name=folder_name)
        copy_staging(folder_name=folder_name)
        return True
    else:
        print('No changes have been made to staging area, commit was not carried out')
        return False


if check_for_wit():
    images_path = get_wit_path(keyword='images')
    staging_path = get_wit_path(keyword='staging_area')
    wit_path = get_wit_path()
