def markdown_to_blocks(markdown) -> list[str]:
    blocks = markdown.split("\n\n")
    sanitised_blocks = []
    for block in blocks:
        sanitised_block = block.strip()
        if sanitised_block != "":
            sanitised_blocks.append(sanitised_block)
    return sanitised_blocks
