from markdown import generate_page
from static_copy import static_copy
from textnode import TextNode, TextType


def main():
    t_node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(t_node)
    static_copy()
    generate_page("./content/index.md", "./template.html", "./public/index.html")


if __name__ == "__main__":
    main()
