from htmlnode import HTMLNode


class ParentNode(HTMLNode):
    def __init__(
            self,
            tag: str | None,
            children: list["HTMLNode"] | None,
            props: dict[str, str] | None = None,
    ):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError()

        if self.children is None or len(self.children) == 0:
            raise ValueError()

        html = f"<{self.tag}{self.props_to_html()}>"

        for child in self.children:
            html += child.to_html()

        html += f"</{self.tag}>"
        return html

    def __repr__(self) -> str:
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
