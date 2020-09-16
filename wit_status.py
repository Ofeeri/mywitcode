# upload 173
import hashlib
import os


class NoWitError(Exception):
    pass


def check_for_wit():
    for _, dirs, _ in os.walk(os.getcwd()):
        for d in dirs:
            if d == '.wit':
                return True
    return False


def get_wit_path(keyword=None):
    """returns accurate path for wit folder, keyword can be 'images' or 'staging_area' because
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


def get_path_outside_wit(filename):
    """return path for a filename that is outside of .wit folder"""
    create_path = False
    for root, dirs, files in os.walk(os.getcwd()):
        for d in dirs:
            if d == filename:
                create_path = True
        for f in files:
            if f == filename:
                create_path = True
        if create_path:
            path = os.path.join(root, filename)
            if 'staging_area' not in path and 'images' not in path and '.wit' not in path:
                if os.path.exists(path):
                    return path


def get_staging_path_objects(names_only=False):
    staging_paths = []

    for root, dirs, files in os.walk(staging_path):
        for f in files:
            path = os.path.join(root, f)
            staging_paths.append(path)
        for d in dirs:
            path = os.path.join(root, d)
            staging_paths.append(path)
    if names_only:
        staging_paths = [os.path.basename(p) for p in staging_paths]
    return staging_paths


def get_current_commit_id():
    refs_path = os.path.join(f'''{get_wit_path()}\\references.txt''')
    with open(refs_path, 'r') as refs:
        current_id = refs.readlines()[0].strip('\n')[5:]
    return current_id


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


def get_file_hash(file_path):
    """create hash for a specific file"""
    with open(file_path, 'rb') as f:
        file_name = os.path.basename(file_path)
        to_hash = f.read() + file_name.encode('utf-8')
        new_hash = hashlib.md5(to_hash).hexdigest()
    return new_hash


def staging_hash_decoder(h):
    """gets path in staging area by its hash"""
    for path in staging_objects:
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                file_name = os.path.basename(path)
                to_hash = f.read() + file_name.encode('utf-8')
                staging_hash = hashlib.md5(to_hash).hexdigest()
                if h == staging_hash:
                    return path
        if os.path.isdir(path):
            folder_name = os.path.basename(path)
            folder_hash = hashlib.md5(folder_name.encode('utf-8')).hexdigest()
            if h == folder_hash:
                return path


def get_deleted_objects():
    """compares all staging area to cwd, deals with cases in which empty folders are added or cases in which
        files or folders are deleted"""
    main_objects = set()
    deleted_objects = []
    for _, dirs, files in os.walk(os.getcwd()):
        for d in dirs:
            obj_path = get_path_outside_wit(d)
            if obj_path:
                main_objects.add(d)
        for f in files:
            obj_path = get_path_outside_wit(f)
            if obj_path:
                main_objects.add(f)
    for o in staging_obj_names:
        if o not in main_objects:
            deleted_objects.append(o)
    return deleted_objects


def get_files_to_be_committed():
    """returns list of files in staging area that have not yet been committed or have been changed since last commit
    by comparing hashes of files in staging area against hashes of files in head folder under .wit\\images"""
    current_staging_hashes = get_all_path_hashes(staging_path)
    head_path = get_wit_path(keyword=get_current_commit_id())
    head_hashes = get_all_path_hashes(path=head_path)
    new_file_hashes = []
    files_to_be_committed = []
    for staging_hash in current_staging_hashes:
        if staging_hash not in head_hashes:
            new_file_hashes.append(staging_hash)
        files_to_be_committed = [staging_hash_decoder(h) for h in new_file_hashes]
    return files_to_be_committed


def get_files_not_staged():
    """returns list of files that are in
        staging area and simultaneously outside of staging area with same name whose contents outside staging differ
        from contents inside staging area."""
    unstaged_files = []
    current_staging_hashes = get_all_path_hashes(staging_path)
    for root, _, files in os.walk(os.getcwd()):
        for f in files:
            file_path = get_path_outside_wit(filename=f)
            if 'staging_area' in root and file_path:
                file_hash = get_file_hash(file_path=file_path)
                if file_hash not in current_staging_hashes:
                    unstaged_files.append(file_path)
    return unstaged_files


def get_untracked_files():
    """returns a list of files in the cwd which are not in staging area"""
    untracked_files = set()
    for _, dirs, files in os.walk(os.getcwd()):
        for d in dirs:
            if d not in staging_obj_names:
                file_path = get_path_outside_wit(filename=d.strip())
                if file_path:
                    untracked_files.add(file_path)
        for f in files:
            if f not in staging_obj_names:
                file_path = get_path_outside_wit(filename=f.strip())
                if file_path:
                    untracked_files.add(file_path)
    return untracked_files


def status():
    """Prints information about relevant files in cwd with .wit folder in the cwd. Prints the current commit Id,
        files in staging area that have not yet been committed or have been changed since last commit and files that are in
        staging area and simultaneously outside of staging area with same name whose contents outside staging differ
        from contents inside staging area."""
    if not check_for_wit():
        raise NoWitError(f'No .wit folder exists in {os.getcwd()}')
    if not os.path.exists(refs_path):
        print('No files have been committed yet')
        return False
    print(f'Current commit ID: {get_current_commit_id()}')
    print('Changes to be committed:')
    print('-' * 20)
    for num, file in enumerate(get_files_to_be_committed()):
        print(f'{num + 1}: {file}')
    print('\n')
    print('Changes not staged for commit')
    print('-' * 20)
    for num, file in enumerate(get_files_not_staged()):
        print(f'{num + 1}: {file}')
    for file in deleted_files:
        print(f'{file} - deleted from main folder')
    print('\n')
    print('Untracked files')
    print('-' * 20)
    for num, file in enumerate(get_untracked_files()):
        print(f'{num + 1}: {file}')


if check_for_wit():
    images_path = get_wit_path(keyword='images')
    staging_path = get_wit_path(keyword='staging_area')
    wit_path = get_wit_path()
    refs_path = os.path.join(f'''{get_wit_path()}\\references.txt''')
    staging_objects = get_staging_path_objects()
    staging_obj_names = get_staging_path_objects(names_only=True)
    deleted_files = get_deleted_objects()
