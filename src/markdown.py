import re
from enum import Enum


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
