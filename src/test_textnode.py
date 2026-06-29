import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNodeEquality(unittest.TestCase):
    def test_eq_same_type_same_text(self):
        self.assertEqual(
            TextNode("This is a text node", TextType.BOLD),
            TextNode("This is a text node", TextType.BOLD),
        )

    def test_ineq_different_type(self):
        self.assertNotEqual(
            TextNode("This is a text node", TextType.BOLD),
            TextNode("This is a text node", TextType.ITALIC),
        )

    def test_ineq_different_text(self):
        self.assertNotEqual(
            TextNode("Hello", TextType.BOLD),
            TextNode("World", TextType.BOLD),
        )

    def test_eq_url_both_none(self):
        # url defaults to None; two plain nodes with the same text are equal
        self.assertEqual(
            TextNode("hello", TextType.PLAIN),
            TextNode("hello", TextType.PLAIN),
        )

    def test_ineq_one_url_none(self):
        self.assertNotEqual(
            TextNode("Click", TextType.LINK, "https://example.com"),
            TextNode("Click", TextType.LINK, None),
        )

    def test_ineq_different_url(self):
        self.assertNotEqual(
            TextNode("Click", TextType.LINK, "https://example.com"),
            TextNode("Click", TextType.LINK, "https://other.com"),
        )

    def test_eq_all_three_fields_match(self):
        self.assertEqual(
            TextNode("Click", TextType.LINK, "https://example.com"),
            TextNode("Click", TextType.LINK, "https://example.com"),
        )


class TestTextNodeRepr(unittest.TestCase):
    def test_repr_no_url(self):
        node = TextNode("hi", TextType.BOLD)
        self.assertEqual(repr(node), "TextNode(hi, bold, None)")

    def test_repr_with_url(self):
        node = TextNode("link", TextType.LINK, "https://x.com")
        self.assertEqual(repr(node), "TextNode(link, link, https://x.com)")

    def test_repr_uses_enum_value_not_name(self):
        # Should print "italic" not "ITALIC"
        node = TextNode("em", TextType.ITALIC)
        self.assertIn("italic", repr(node))
        self.assertNotIn("ITALIC", repr(node))

    def test_repr_starts_with_class_name(self):
        node = TextNode("x", TextType.PLAIN)
        self.assertTrue(repr(node).startswith("TextNode("))


class TestConvertPlain(unittest.TestCase):
    def setUp(self):
        self.node = text_node_to_html_node(TextNode("hello world", TextType.PLAIN))

    def test_tag_is_none(self):
        self.assertIsNone(self.node.tag)

    def test_value_preserved(self):
        self.assertEqual(self.node.value, "hello world")

    def test_no_props(self):
        self.assertIsNone(self.node.props)

    def test_to_html_returns_raw_text(self):
        self.assertEqual(self.node.to_html(), "hello world")


class TestConvertBold(unittest.TestCase):
    def setUp(self):
        self.node = text_node_to_html_node(TextNode("important", TextType.BOLD))

    def test_tag_is_b(self):
        self.assertEqual(self.node.tag, "b")

    def test_value_preserved(self):
        self.assertEqual(self.node.value, "important")

    def test_no_props(self):
        self.assertIsNone(self.node.props)

    def test_to_html(self):
        self.assertEqual(self.node.to_html(), "<b>important</b>")


class TestConvertItalic(unittest.TestCase):
    def setUp(self):
        self.node = text_node_to_html_node(TextNode("emphasis", TextType.ITALIC))

    def test_tag_is_i(self):
        self.assertEqual(self.node.tag, "i")

    def test_value_preserved(self):
        self.assertEqual(self.node.value, "emphasis")

    def test_no_props(self):
        self.assertIsNone(self.node.props)

    def test_to_html(self):
        self.assertEqual(self.node.to_html(), "<i>emphasis</i>")


class TestConvertCode(unittest.TestCase):
    def setUp(self):
        self.node = text_node_to_html_node(TextNode("print('hi')", TextType.CODE))

    def test_tag_is_code(self):
        self.assertEqual(self.node.tag, "code")

    def test_value_preserved(self):
        self.assertEqual(self.node.value, "print('hi')")

    def test_no_props(self):
        self.assertIsNone(self.node.props)

    def test_to_html(self):
        self.assertEqual(self.node.to_html(), "<code>print('hi')</code>")


class TestConvertLink(unittest.TestCase):
    def setUp(self):
        self.node = text_node_to_html_node(
            TextNode("Click here", TextType.LINK, "https://example.com")
        )

    def test_tag_is_a(self):
        self.assertEqual(self.node.tag, "a")

    def test_value_is_link_text(self):
        self.assertEqual(self.node.value, "Click here")

    def test_href_prop_set(self):
        self.assertEqual(self.node.props["href"], "https://example.com")

    def test_no_extra_props(self):
        self.assertEqual(list(self.node.props.keys()), ["href"])

    def test_to_html(self):
        self.assertEqual(
            self.node.to_html(),
            '<a href="https://example.com">Click here</a>',
        )


class TestConvertImage(unittest.TestCase):
    def setUp(self):
        self.node = text_node_to_html_node(
            TextNode("a cat", TextType.IMAGE, "/assets/cat.png")
        )

    def test_tag_is_img(self):
        self.assertEqual(self.node.tag, "img")

    def test_value_is_none(self):
        # The converter passes value=None for images
        self.assertIsNone(self.node.value)

    def test_src_prop(self):
        self.assertEqual(self.node.props["src"], "/assets/cat.png")

    def test_alt_prop_is_text(self):
        self.assertEqual(self.node.props["alt"], "a cat")

    def test_only_src_and_alt_props(self):
        self.assertEqual(sorted(self.node.props.keys()), ["alt", "src"])

    def test_to_html_raises_because_value_is_none(self):
        with self.assertRaises(ValueError):
            self.node.to_html()


if __name__ == "__main__":
    unittest.main()
