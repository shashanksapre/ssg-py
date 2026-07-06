import os
import shutil


def dir_copy(src_path: str, dest_path: str):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    dir_list = os.listdir(src_path)
    for dir_item in dir_list:
        src_item = os.path.join(src_path, dir_item)
        dest_item = os.path.join(dest_path, dir_item)
        if os.path.isfile(src_item):
            shutil.copy(src_item, dest_item)
        else:
            dir_copy(src_item, dest_item)


def static_copy(src_path: str, dest_path: str):
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    dir_copy(src_path, dest_path)
