from enum import Enum

from helpers import extract_markdown_images, extract_markdown_links
from leafnode import LeafNode


class TextType(Enum):
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: "TextNode") -> bool:
        return (
                self.text == other.text
                and self.text_type.value == other.text_type.value
                and self.url == other.url
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    match text_node.text_type:
        case TextType.PLAIN:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("text_type not supported")


def split_nodes_delimiter(
        old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if not node.text_type == TextType.PLAIN:
            new_nodes.append(node)
        else:
            num_delimiters = node.text.count(delimiter)

            if num_delimiters == 0:
                new_nodes.append(node)
                continue

            if not num_delimiters % 2 == 0:
                raise Exception(f"closing {delimiter} not found.")

            splits = node.text.split(delimiter)

            sub_nodes = []

            for i in range(len(splits)):
                if splits[i] == "":
                    continue
                if i % 2 == 0:
                    sub_nodes.append(TextNode(splits[i], node.text_type))
                else:
                    sub_nodes.append(TextNode(splits[i], text_type))

            new_nodes.extend(sub_nodes)

    return new_nodes


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if not node.text_type == TextType.PLAIN:
            new_nodes.append(node)
        else:
            images = extract_markdown_images(node.text)

            if len(images) == 0:
                new_nodes.append(node)
                continue

            current_text = node.text
            sub_nodes = []

            for image in images:
                sections = current_text.split(f"![{image[0]}]({image[1]})", 1)

                if sections[0] != "":
                    sub_nodes.append(TextNode(sections[0], node.text_type))

                sub_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
                current_text = sections[1]

            new_nodes.extend(sub_nodes)

            if current_text != "":
                new_nodes.append(TextNode(current_text, TextType.PLAIN))

    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if not node.text_type == TextType.PLAIN:
            new_nodes.append(node)
        else:
            links = extract_markdown_links(node.text)

            if len(links) == 0:
                new_nodes.append(node)
                continue

            current_text = node.text
            sub_nodes = []

            for link in links:
                sections = current_text.split(f"[{link[0]}]({link[1]})", 1)

                if sections[0] != "":
                    sub_nodes.append(TextNode(sections[0], node.text_type))

                sub_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
                current_text = sections[1]

            new_nodes.extend(sub_nodes)

            if current_text != "":
                new_nodes.append(TextNode(current_text, TextType.PLAIN))

    return new_nodes


def text_to_textnodes(text) -> list[TextNode]:
    nodes = [TextNode(text, TextType.PLAIN)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes
