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
        node = HTMLNode(tag="section")
        self.assertEqual(node.tag, "section")

    def test_value(self):
        node = HTMLNode(value="Hello, world!")
        self.assertEqual(node.value, "Hello, world!")

    def test_single_child(self):
        child = HTMLNode(tag="span", value="inner")
        node = HTMLNode(tag="div", children=[child])
        self.assertEqual(len(node.children), 1)
        self.assertIs(node.children[0], child)

    def test_multiple_children(self):
        children = [HTMLNode(tag="li", value=str(i)) for i in range(3)]
        node = HTMLNode(tag="ul", children=children)
        self.assertEqual(len(node.children), 3)

    def test_nested_children(self):
        grandchild = HTMLNode(tag="b", value="bold")
        child = HTMLNode(tag="p", children=[grandchild])
        parent = HTMLNode(tag="div", children=[child])
        self.assertIs(parent.children[0].children[0], grandchild)

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
            props={"class": "container"},
        )
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "outer")
        self.assertEqual(node.children, [child])
        self.assertEqual(node.props["class"], "container")


class TestHTMLNodePropsToHtml(unittest.TestCase):
    def test_none_props_returns_empty_string(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_empty_props_returns_empty_string(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_single_prop_format(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com"')

    def test_single_prop_has_leading_space(self):
        node = HTMLNode(tag="p", props={"class": "intro"})
        self.assertTrue(node.props_to_html().startswith(" "))

    def test_prop_value_is_quoted(self):
        node = HTMLNode(tag="p", props={"id": "main"})
        self.assertIn('"main"', node.props_to_html())

    def test_multiple_props_each_present(self):
        node = HTMLNode(
            tag="a", props={"href": "https://example.com", "target": "_blank"}
        )
        result = node.props_to_html()
        self.assertIn('href="https://example.com"', result)
        self.assertIn('target="_blank"', result)

    def test_multiple_props_space_separated(self):
        node = HTMLNode(
            tag="a", props={"href": "https://example.com", "target": "_blank"}
        )
        result = node.props_to_html().strip()
        # After stripping the leading space each pair should be separated by a space
        pairs = result.split(" ")
        self.assertEqual(len(pairs), 2)


class TestHTMLNodeToHtml(unittest.TestCase):
    def test_raises_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_raises_not_implemented_with_full_node(self):
        node = HTMLNode(tag="div", value="content", props={"class": "box"})
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestHTMLNodeRepr(unittest.TestCase):
    def test_repr_no_args(self):
        node = HTMLNode()
        self.assertEqual(repr(node), "HTMLNode(None, None, children: None, None)")

    def test_repr_with_tag_and_value(self):
        node = HTMLNode(tag="p", value="text")
        rep = repr(node)
        self.assertIn("p", rep)
        self.assertIn("text", rep)

    def test_repr_contains_children_label(self):
        node = HTMLNode(tag="div", children=[HTMLNode(tag="span")])
        self.assertIn("children:", repr(node))

    def test_repr_contains_props(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com"})
        rep = repr(node)
        self.assertIn("href", rep)
        self.assertIn("https://example.com", rep)

    def test_repr_starts_and_ends_correctly(self):
        node = HTMLNode(tag="div")
        rep = repr(node)
        self.assertTrue(rep.startswith("HTMLNode("))
        self.assertTrue(rep.endswith(")"))


if __name__ == "__main__":
    unittest.main()
