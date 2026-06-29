class HTMLNode:
    def __init__(
            self,
            tag: str | None = None,
            value: str | None = None,
            children: list["HTMLNode"] | None = None,
            props: dict[str, str] | None = None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if self.props is not None:
            props_list = []
            for key in self.props:
                props_list.append(f"{key}={self.props[key]}")
            return " ".join(props_list)
        else:
            return ""

    def __repr__(self) -> str:
        rep = "HTMLNode("
        if self.tag is not None:
            rep += f", {self.tag}"
        if self.value is not None:
            rep += f", {self.value}"
        if self.children is not None:
            rep += f", {self.children}"
        if self.props is not None:
            rep += f", {self.props}"
        return f"{rep})"
