from generate_content import generate_site
from static_copy import static_copy
from textnode import TextNode, TextType


def main():
    t_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(t_node)
    static_copy()
    generate_site(src_path="./content", dest_path="./public")


if __name__ == "__main__":
    main()
