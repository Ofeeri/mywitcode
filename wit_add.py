# upload 171
import os
import shutil


class NoWitError(Exception):
    pass


def check_for_wit():
    for _, dirs, _ in os.walk(os.getcwd()):
        for d in dirs:
            if d == '.wit':
                return True
    return False


def get_wit_path():
    path = 'none'
    for root, dirs, _ in os.walk(os.getcwd()):
        for d in dirs:
            if d == '.wit':
                path = os.path.join(root, d)
    return path


def add(filename):
    if not check_for_wit():
        raise NoWitError(f'No .wit folder exists in {os.getcwd()}')
    if not os.path.exists(filename):
        print(f'{filename} does not exist')
        raise IOError
    staging_area = os.path.join(f'{get_wit_path()}\\staging_area')
    if os.path.isfile(filename):
        shutil.copy(filename, staging_area)
    if os.path.isdir(filename):
        destination = f'{staging_area}\\{filename}'
        try:
            shutil.copytree(src=filename, dst=destination)
        except FileExistsError:
            shutil.rmtree(destination)
            shutil.copytree(src=filename, dst=destination)
