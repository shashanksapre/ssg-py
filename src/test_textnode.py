import unittest

from textnode import TextNode, TextType, text_node_to_html_node, split_nodes_delimiter


def types(nodes: list[TextNode]) -> list[TextType]:
    return [n.text_type for n in nodes]


def texts(nodes: list[TextNode]) -> list[str]:
    return [n.text for n in nodes]


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


class TestSplitNodesPassthrough(unittest.TestCase):
    def test_empty_list_returns_empty(self):
        self.assertEqual(split_nodes_delimiter([], "**", TextType.BOLD), [])

    def test_plain_node_with_no_delimiter_unchanged(self):
        node = TextNode("just plain text", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just plain text")
        self.assertEqual(result[0].text_type, TextType.PLAIN)

    def test_plain_node_empty_text_unchanged(self):
        node = TextNode("", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "")

    def test_bold_node_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.ITALIC)
        self.assertEqual(result, [node])

    def test_italic_node_passes_through(self):
        node = TextNode("already italic", TextType.ITALIC)
        result = split_nodes_delimiter([node], "*", TextType.BOLD)
        self.assertEqual(result, [node])

    def test_code_node_passes_through(self):
        node = TextNode("x = 1", TextType.CODE)
        result = split_nodes_delimiter([node], "`", TextType.BOLD)
        self.assertEqual(result, [node])

    def test_link_node_passes_through(self):
        node = TextNode("Google", TextType.LINK, "https://google.com")
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result[0].url, "https://google.com")

    def test_image_node_passes_through(self):
        node = TextNode("cat", TextType.IMAGE, "/cat.png")
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [node])

    def test_non_plain_node_containing_delimiter_not_split(self):
        # A BOLD node whose text contains "**" must not be touched
        node = TextNode("**still bold**", TextType.BOLD)
        result = split_nodes_delimiter([node], "**", TextType.ITALIC)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "**still bold**")
        self.assertEqual(result[0].text_type, TextType.BOLD)


class TestSplitNodesBasic(unittest.TestCase):
    def test_delimiter_in_middle(self):
        result = split_nodes_delimiter(
            [TextNode("hello **world** foo", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["hello ", "world", " foo"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.BOLD, TextType.PLAIN])

    def test_delimiter_wraps_entire_text(self):
        # Leading and trailing empty segments are silently dropped
        result = split_nodes_delimiter(
            [TextNode("**bold**", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["bold"])
        self.assertEqual(types(result), [TextType.BOLD])

    def test_delimiter_at_start(self):
        result = split_nodes_delimiter(
            [TextNode("**bold** text", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["bold", " text"])
        self.assertEqual(types(result), [TextType.BOLD, TextType.PLAIN])

    def test_delimiter_at_end(self):
        result = split_nodes_delimiter(
            [TextNode("text **bold**", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["text ", "bold"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.BOLD])

    def test_code_delimiter(self):
        result = split_nodes_delimiter(
            [TextNode("use `x = 1` here", TextType.PLAIN)], "`", TextType.CODE
        )
        self.assertEqual(texts(result), ["use ", "x = 1", " here"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.CODE, TextType.PLAIN])

    def test_italic_delimiter(self):
        result = split_nodes_delimiter(
            [TextNode("some *italic* word", TextType.PLAIN)], "*", TextType.ITALIC
        )
        self.assertEqual(texts(result), ["some ", "italic", " word"])
        self.assertEqual(
            types(result), [TextType.PLAIN, TextType.ITALIC, TextType.PLAIN]
        )

    def test_child_nodes_have_none_url(self):
        result = split_nodes_delimiter(
            [TextNode("text **bold** more", TextType.PLAIN)], "**", TextType.BOLD
        )
        for node in result:
            self.assertIsNone(node.url)

    def test_output_length_single_section(self):
        result = split_nodes_delimiter(
            [TextNode("a **b** c", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(len(result), 3)


class TestSplitNodesMultipleSections(unittest.TestCase):
    def test_two_delimited_sections(self):
        result = split_nodes_delimiter(
            [TextNode("a **b** c **d** e", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["a ", "b", " c ", "d", " e"])
        self.assertEqual(
            types(result),
            [
                TextType.PLAIN,
                TextType.BOLD,
                TextType.PLAIN,
                TextType.BOLD,
                TextType.PLAIN,
            ],
        )

    def test_three_delimited_sections(self):
        result = split_nodes_delimiter(
            [TextNode("a **b** c **d** e **f** g", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["a ", "b", " c ", "d", " e ", "f", " g"])

    def test_adjacent_sections_empty_middle_dropped(self):
        # "**a****b**" splits to ["", "a", "", "b", ""] — empty segs dropped
        result = split_nodes_delimiter(
            [TextNode("**a****b**", TextType.PLAIN)], "**", TextType.BOLD
        )
        self.assertEqual(texts(result), ["a", "b"])
        self.assertEqual(types(result), [TextType.BOLD, TextType.BOLD])


# ---------------------------------------------------------------------------
# split_nodes_delimiter — mixed node lists
# ---------------------------------------------------------------------------


class TestSplitNodesMixedList(unittest.TestCase):
    def test_plain_and_non_plain_interleaved(self):
        nodes = [
            TextNode("hello **world**", TextType.PLAIN),
            TextNode("already bold", TextType.BOLD),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(texts(result), ["hello ", "world", "already bold"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.BOLD, TextType.BOLD])

    def test_plain_node_without_delimiter_left_intact_among_others(self):
        nodes = [
            TextNode("hello **world**", TextType.PLAIN),
            TextNode("no markers here", TextType.PLAIN),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(texts(result), ["hello ", "world", "no markers here"])

    def test_chained_bold_then_italic(self):
        # Simulates a two-pass markdown parsing pipeline
        nodes = [TextNode("**bold** and *italic* text", TextType.PLAIN)]
        after_bold = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        after_italic = split_nodes_delimiter(after_bold, "*", TextType.ITALIC)
        self.assertEqual(texts(after_italic), ["bold", " and ", "italic", " text"])
        self.assertEqual(
            types(after_italic),
            [TextType.BOLD, TextType.PLAIN, TextType.ITALIC, TextType.PLAIN],
        )

    def test_output_order_matches_input_order(self):
        nodes = [
            TextNode("first **A**", TextType.PLAIN),
            TextNode("second **B**", TextType.PLAIN),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(texts(result), ["first ", "A", "second ", "B"])

    def test_only_non_plain_nodes_all_pass_through(self):
        nodes = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(len(result), 3)
        self.assertEqual(types(result), [TextType.BOLD, TextType.ITALIC, TextType.CODE])


class TestSplitNodesErrors(unittest.TestCase):
    def test_unclosed_delimiter_raises(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter(
                [TextNode("hello **world", TextType.PLAIN)], "**", TextType.BOLD
            )

    def test_single_delimiter_character_raises(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter([TextNode("*", TextType.PLAIN)], "*", TextType.ITALIC)

    def test_three_occurrences_raises(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter(
                [TextNode("**a** **b** **c", TextType.PLAIN)], "**", TextType.BOLD
            )

    def test_exception_message_contains_delimiter(self):
        with self.assertRaises(Exception) as ctx:
            split_nodes_delimiter(
                [TextNode("unclosed **tag", TextType.PLAIN)], "**", TextType.BOLD
            )
        self.assertIn("**", str(ctx.exception))

    def test_bad_node_in_list_raises_before_later_nodes(self):
        with self.assertRaises(Exception):
            split_nodes_delimiter(
                [
                    TextNode("bad **unclosed", TextType.PLAIN),
                    TextNode("ok **closed**", TextType.PLAIN),
                ],
                "**",
                TextType.BOLD,
            )


if __name__ == "__main__":
    unittest.main()
