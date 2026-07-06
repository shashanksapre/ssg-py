import os
from pathlib import Path

from markdown import markdown_to_html_node, extract_title


def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as f:
        markdown = f.read()
        f.close()

    with open(template_path, "r") as f:
        template = f.read()
        f.close()

    h_node = markdown_to_html_node(markdown)
    html = h_node.to_html()
    title = extract_title(markdown)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(template)


def generate_site(src_path: str, dest_path: str):
    dir_list = os.listdir(src_path)
    for dir_item in dir_list:
        src_item = os.path.join(src_path, dir_item)
        dest_item = os.path.join(dest_path, dir_item)

        if os.path.isfile(src_item):
            generate_page(
                src_item, "./template.html", Path(dest_item).with_suffix(".html")
            )
        else:
            generate_site(src_item, dest_item)
