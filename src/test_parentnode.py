import unittest

from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNodeInit(unittest.TestCase):
    def test_value_always_none(self):
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsNone(node.value)

    def test_tag_stored(self):
        node = ParentNode("section", [LeafNode("p", "text")])
        self.assertEqual(node.tag, "section")

    def test_children_stored(self):
        children = [LeafNode("li", "a"), LeafNode("li", "b")]
        node = ParentNode("ul", children)
        self.assertEqual(node.children, children)

    def test_props_default_none(self):
        node = ParentNode("div", [LeafNode("p", "text")])
        self.assertIsNone(node.props)

    def test_props_stored(self):
        node = ParentNode("div", [LeafNode("p", "text")], {"class": "box"})
        self.assertEqual(node.props["class"], "box")


class TestParentNodeToHtmlValueErrors(unittest.TestCase):
    def test_none_tag_raises(self):
        node = ParentNode(None, [LeafNode("p", "text")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_none_children_raises(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_empty_children_raises(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()


class TestParentNodeToHtmlStructure(unittest.TestCase):
    def test_single_child(self):
        node = ParentNode("div", [LeafNode("span", "child")])
        self.assertEqual(node.to_html(), "<div><span>child</span></div>")

    def test_multiple_children_ordered(self):
        node = ParentNode(
            "ul",
            [
                LeafNode("li", "one"),
                LeafNode("li", "two"),
                LeafNode("li", "three"),
            ],
        )
        self.assertEqual(
            node.to_html(), "<ul><li>one</li><li>two</li><li>three</li></ul>"
        )

    def test_grandchildren(self):
        node = ParentNode(
            "div",
            [
                ParentNode("span", [LeafNode("b", "grandchild")]),
            ],
        )
        self.assertEqual(node.to_html(), "<div><span><b>grandchild</b></span></div>")

    def test_three_levels_deep(self):
        node = ParentNode(
            "div",
            [
                ParentNode(
                    "section",
                    [
                        ParentNode("p", [LeafNode("b", "deep")]),
                    ],
                ),
            ],
        )
        self.assertEqual(
            node.to_html(), "<div><section><p><b>deep</b></p></section></div>"
        )

    def test_mixed_parent_and_leaf_siblings(self):
        node = ParentNode(
            "div",
            [
                ParentNode("p", [LeafNode("b", "bold")]),
                LeafNode("span", "plain"),
            ],
        )
        self.assertEqual(
            node.to_html(), "<div><p><b>bold</b></p><span>plain</span></div>"
        )

    def test_tagless_leaf_child_renders_raw_text(self):
        node = ParentNode("p", [LeafNode(None, "raw text")])
        self.assertEqual(node.to_html(), "<p>raw text</p>")

    def test_output_starts_with_opening_tag(self):
        node = ParentNode("article", [LeafNode("p", "text")])
        self.assertTrue(node.to_html().startswith("<article>"))

    def test_output_ends_with_closing_tag(self):
        node = ParentNode("article", [LeafNode("p", "text")])
        self.assertTrue(node.to_html().endswith("</article>"))


class TestParentNodeToHtmlWithProps(unittest.TestCase):
    def test_single_prop_on_parent(self):
        node = ParentNode("div", [LeafNode("p", "text")], {"class": "container"})
        self.assertEqual(node.to_html(), '<div class="container"><p>text</p></div>')

    def test_multiple_props_on_parent(self):
        node = ParentNode(
            "div", [LeafNode("p", "text")], {"class": "container", "id": "main"}
        )
        result = node.to_html()
        self.assertIn('class="container"', result)
        self.assertIn('id="main"', result)
        self.assertTrue(result.endswith("<p>text</p></div>"))

    def test_props_not_leaked_to_children(self):
        child = LeafNode("p", "text")
        ParentNode("div", [child], {"class": "box"}).to_html()
        # Child props unchanged after parent renders
        self.assertIsNone(child.props)

    def test_props_on_nested_parent(self):
        node = ParentNode(
            "div",
            [
                ParentNode("span", [LeafNode("b", "hi")], {"class": "inner"}),
            ],
        )
        self.assertEqual(
            node.to_html(), '<div><span class="inner"><b>hi</b></span></div>'
        )


class TestParentNodeRepr(unittest.TestCase):

    def test_repr_mistakenly_says_leafnode(self):
        node = ParentNode("div", [LeafNode("span", "x")])
        self.assertTrue(repr(node).startswith("LeafNode("))

    def test_repr_contains_tag(self):
        node = ParentNode("div", [LeafNode("span", "x")])
        self.assertIn("div", repr(node))

    def test_repr_value_is_none(self):
        node = ParentNode("div", [LeafNode("span", "x")])
        self.assertIn("None", repr(node))


if __name__ == "__main__":
    unittest.main()
