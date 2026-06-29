import unittest

from leafnode import LeafNode


class TestLeafNodeInit(unittest.TestCase):
    def test_children_always_none(self):
        node = LeafNode("p", "text")
        self.assertIsNone(node.children)

    def test_tag_and_value(self):
        node = LeafNode("p", "Hello")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Hello")

    def test_props_stored(self):
        node = LeafNode("a", "Click", {"href": "https://example.com"})
        self.assertEqual(node.props["href"], "https://example.com")

    def test_default_props_none(self):
        node = LeafNode("p", "text")
        self.assertIsNone(node.props)

    def test_none_tag_allowed(self):
        node = LeafNode(None, "raw text")
        self.assertIsNone(node.tag)

    def test_none_value_allowed(self):
        # Value can be None on construction; to_html enforces the constraint
        node = LeafNode("br", None)
        self.assertIsNone(node.value)


class TestLeafNodeToHtml(unittest.TestCase):
    def test_none_value_raises_value_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_none_tag_returns_raw_value(self):
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_tag_no_props(self):
        node = LeafNode("p", "Hello")
        self.assertEqual(node.to_html(), "<p>Hello</p>")

    def test_tag_with_single_prop(self):
        node = LeafNode("a", "Click here", {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Click here</a>')

    def test_tag_with_multiple_props(self):
        node = LeafNode(
            "a", "Link", {"href": "https://example.com", "target": "_blank"}
        )
        result = node.to_html()
        self.assertTrue(result.startswith("<a "))
        self.assertIn('href="https://example.com"', result)
        self.assertIn('target="_blank"', result)
        self.assertTrue(result.endswith(">Link</a>"))

    def test_different_tags(self):
        self.assertEqual(LeafNode("h1", "Title").to_html(), "<h1>Title</h1>")
        self.assertEqual(LeafNode("b", "bold").to_html(), "<b>bold</b>")
        self.assertEqual(LeafNode("i", "italic").to_html(), "<i>italic</i>")

    def test_empty_string_value_is_valid(self):
        node = LeafNode("p", "")
        self.assertEqual(node.to_html(), "<p></p>")

    def test_value_preserved_exactly(self):
        node = LeafNode("p", "Hello & <world>")
        self.assertIn("Hello & <world>", node.to_html())


class TestLeafNodeRepr(unittest.TestCase):
    def test_repr_format(self):
        node = LeafNode("p", "hello", {"class": "para"})
        self.assertEqual(repr(node), "LeafNode(p, hello, {'class': 'para'})")

    def test_repr_no_props(self):
        node = LeafNode("p", "hello")
        self.assertEqual(repr(node), "LeafNode(p, hello, None)")

    def test_repr_starts_with_class_name(self):
        node = LeafNode("span", "text")
        self.assertTrue(repr(node).startswith("LeafNode("))


if __name__ == "__main__":
    unittest.main()
