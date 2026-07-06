import os

from markdown import generate_page
from static_copy import static_copy
from textnode import TextNode, TextType


def generate_site(src_path: str, dest_path: str):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    dir_list = os.listdir(src_path)
    for dir_item in dir_list:
        src_item = os.path.join(src_path, dir_item)
        dest_item = os.path.join(dest_path, dir_item)
        if os.path.isfile(src_item):
            generate_page(
                src_item, "./template.html", dest_item.replace(".md", ".html")
            )
        else:
            generate_site(src_item, dest_item)


def main():
    t_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(t_node)
    static_copy()
    generate_site(src_path="./content", dest_path="./public")


if __name__ == "__main__":
    main()
