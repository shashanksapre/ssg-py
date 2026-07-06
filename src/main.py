import os
import shutil

from textnode import TextNode, TextType


def dir_copy(src_path: str, dest_path: str):
    dir_list = os.listdir(src_path)
    for dir_item in dir_list:
        print(f"processing {dir_item}")
        src_item = os.path.join(src_path, dir_item)
        dest_item = os.path.join(dest_path, dir_item)
        if os.path.isfile(os.path.join(src_path, dir_item)):
            shutil.copy(src_item, dest_item)
            print(f"copied {src_item} to {dest_item}")
        else:
            os.mkdir(dest_item)
            dir_copy(src_item, dest_item)


def static_copy():
    if os.path.exists("./static"):
        print("static exists")
        shutil.rmtree("./public")
        print("removed public")
        os.mkdir("./public")
        print("created public")
        dir_copy("./static", "./public")
        print("copied static to public")
    else:
        print("static dir does not exist")


def main():
    t_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    static_copy()
    print(t_node)


if __name__ == "__main__":
    main()
