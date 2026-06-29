import unittest

from htmlnode import HTMLNode


class TestHTMLNodeInit(unittest.TestCase):
    def test_all_defaults_are_none(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_tag(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.tag, "p")

    def test_value(self):
        node = HTMLNode(value="Hello, world!")
        self.assertEqual(node.value, "Hello, world!")

    def test_children(self):
        child = HTMLNode(tag="span", value="child text")
        node = HTMLNode(tag="div", children=[child])
        self.assertEqual(len(node.children), 1)
        self.assertIs(node.children[0], child)

    def test_multiple_children(self):
        children = [HTMLNode(tag="li", value=str(i)) for i in range(3)]
        node = HTMLNode(tag="ul", children=children)
        self.assertEqual(len(node.children), 3)

    def test_props(self):
        props = {"href": "https://example.com", "target": "_blank"}
        node = HTMLNode(tag="a", props=props)
        self.assertEqual(node.props, props)

    def test_all_params(self):
        child = HTMLNode(tag="span", value="inner")
        node = HTMLNode(
            tag="div",
            value="outer",
            children=[child],
            props={"class": "container", "id": "main"},
        )
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "outer")
        self.assertEqual(node.children, [child])
        self.assertEqual(node.props["class"], "container")
        self.assertEqual(node.props["id"], "main")

    def test_nested_children(self):
        grandchild = HTMLNode(tag="b", value="bold")
        child = HTMLNode(tag="p", children=[grandchild])
        parent = HTMLNode(tag="div", children=[child])
        self.assertIs(parent.children[0].children[0], grandchild)


class TestHTMLNodePropsToHtml(unittest.TestCase):
    def test_none_props_returns_empty_string(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_empty_props_returns_empty_string(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    # NOTE: The following tests expose a bug in props_to_html.
    # props_list is checked with `if len(props_list) == 0: return ""`
    # immediately after being initialised as [], so the for-loop never
    # runs and the method always returns "" — even when props is populated.
    # These tests document the *intended* behaviour and will fail until the
    # bug is fixed by moving (or removing) that early-exit check.

    def test_single_prop(self):
        node = HTMLNode(tag="img", props={"src": "/image.png"})
        self.assertEqual(node.props_to_html(), "src=/image.png")

    def test_multiple_props_contains_each_pair(self):
        node = HTMLNode(
            tag="a", props={"href": "https://example.com", "target": "_blank"}
        )
        result = node.props_to_html()
        self.assertIn("href=https://example.com", result)
        self.assertIn("target=_blank", result)

    def test_multiple_props_are_space_separated(self):
        node = HTMLNode(
            tag="a", props={"href": "https://example.com", "target": "_blank"}
        )
        result = node.props_to_html()
        # Each key=value pair should be separated by exactly one space
        pairs = result.split(" ")
        self.assertEqual(len(pairs), 2)

    def test_props_with_class(self):
        node = HTMLNode(tag="div", props={"class": "hero"})
        self.assertEqual(node.props_to_html(), "class=hero")


class TestHTMLNodeToHtml(unittest.TestCase):
    def test_raises_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_raises_not_implemented_with_tag(self):
        node = HTMLNode(tag="div", value="content")
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestHTMLNodeRepr(unittest.TestCase):
    def test_repr_no_args(self):
        node = HTMLNode()
        self.assertEqual(repr(node), "HTMLNode()")

    def test_repr_contains_tag(self):
        node = HTMLNode(tag="p")
        self.assertIn("p", repr(node))

    def test_repr_contains_value(self):
        node = HTMLNode(value="hello")
        self.assertIn("hello", repr(node))

    def test_repr_contains_props(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com"})
        rep = repr(node)
        self.assertIn("href", rep)
        self.assertIn("https://example.com", rep)

    def test_repr_contains_children(self):
        child = HTMLNode(tag="span")
        node = HTMLNode(tag="div", children=[child])
        self.assertIn("span", repr(node))

    def test_repr_starts_with_class_name(self):
        node = HTMLNode(tag="div")
        self.assertTrue(repr(node).startswith("HTMLNode("))

    def test_repr_ends_with_paren(self):
        node = HTMLNode(tag="div", value="text")
        self.assertTrue(repr(node).endswith(")"))


if __name__ == "__main__":
    unittest.main()
