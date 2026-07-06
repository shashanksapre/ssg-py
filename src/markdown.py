import re
from enum import Enum

from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode
from textnode import text_to_textnodes, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown) -> list[str]:
    blocks = markdown.split("\n\n")
    sanitised_blocks = []
    for block in blocks:
        sanitised_block = block.strip()
        if sanitised_block != "":
            sanitised_blocks.append(sanitised_block)
    return sanitised_blocks


def block_to_block_type(block: str) -> BlockType:
    match_heading = re.match(r"^#{1,6}\s.*$", block)

    if match_heading is not None:
        return BlockType.HEADING

    lines = block.split("\n")
    match_code = lines[0].startswith("```") and lines[-1].startswith("```")

    if len(lines) >= 3 and match_code:
        return BlockType.CODE

    match_quote = re.match(r"^>.*", block)

    if match_quote is not None:
        lines = block.split("\n")

        if all(re.match(r"^>.*", line) is not None for line in lines):
            return BlockType.QUOTE

    match_ul = re.match(r"^-\s.*", block)

    if match_ul is not None:
        lines = block.split("\n")

        if all(re.match(r"^-\s.*", line) is not None for line in lines):
            return BlockType.UNORDERED_LIST

    match_first_ol = re.match(r"^1\.\s.*", block)

    if match_first_ol is not None:
        lines = block.split("\n")
        is_ol = True

        for i in range(len(lines)):
            serial = i + 1
            if not re.match(rf"^{serial}\.\s.*", lines[i]):
                is_ol = False

        if is_ol:
            return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown) -> HTMLNode:
    blocks = markdown_to_blocks(markdown)

    child_nodes: list[ParentNode | LeafNode] = []

    for block in blocks:
        b_type = block_to_block_type(block)

        match b_type:
            case BlockType.QUOTE:
                lines = block.split("\n")
                stripped_lines: list[str] = []
                for line in lines:
                    stripped_lines.append(line.lstrip(">").strip())
                content = " ".join(stripped_lines)
                quote_text_nodes = text_to_textnodes(content)
                quote_html_nodes: list[LeafNode] = []
                for quote_text_node in quote_text_nodes:
                    quote_html_nodes.append(text_node_to_html_node(quote_text_node))
                child_nodes.append(ParentNode("blockquote", quote_html_nodes))
            case BlockType.CODE:
                code_block = LeafNode("code", block[4:-3])
                pre_block = ParentNode("pre", [code_block])
                child_nodes.append(pre_block)
            case BlockType.PARAGRAPH:
                paragraph_text_nodes = text_to_textnodes(
                    " ".join(line.strip() for line in block.split("\n"))
                )
                paragraph_html_nodes: list[LeafNode] = []
                for paragraph_text_node in paragraph_text_nodes:
                    paragraph_html_nodes.append(
                        text_node_to_html_node(paragraph_text_node)
                    )
                child_nodes.append(ParentNode("p", paragraph_html_nodes))
            case BlockType.HEADING:
                hash_count = block.split(" ")[0].count("#")
                heading_text_nodes = text_to_textnodes(block.split(" ", 1)[1])
                heading_html_nodes: list[LeafNode] = []
                for heading_text_node in heading_text_nodes:
                    heading_html_nodes.append(text_node_to_html_node(heading_text_node))
                child_nodes.append(ParentNode(f"h{hash_count}", heading_html_nodes))
            case BlockType.UNORDERED_LIST:
                lines = block.split("\n")
                list_items: list[ParentNode] = []
                for line in lines:
                    line_text_nodes = text_to_textnodes(line.split("- ", 1)[1])
                    line_html_nodes: list[LeafNode] = []
                    for line_text_node in line_text_nodes:
                        line_html_nodes.append(text_node_to_html_node(line_text_node))
                    list_items.append(ParentNode("li", line_html_nodes))
                child_nodes.append(ParentNode("ul", list_items))
            case BlockType.ORDERED_LIST:
                lines = block.split("\n")
                list_items: list[ParentNode] = []
                for line in lines:
                    line_text_nodes = text_to_textnodes(line.split(". ", 1)[1])
                    line_html_nodes: list[LeafNode] = []
                    for line_text_node in line_text_nodes:
                        line_html_nodes.append(text_node_to_html_node(line_text_node))
                    list_items.append(ParentNode("li", line_html_nodes))
                child_nodes.append(ParentNode("ol", list_items))

    return ParentNode("div", child_nodes)


def extract_title(markdown: str) -> str:
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block.split("# ", 1)[1]
    raise Exception("Didn't find any Heading")
