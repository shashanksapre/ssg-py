import unittest

from textnode import TextNode, TextType, text_to_textnodes


def types(nodes: list[TextNode]) -> list[TextType]:
    return [n.text_type for n in nodes]


def texts(nodes: list[TextNode]) -> list[str]:
    return [n.text for n in nodes]


class TestTextToTextNodesTrivial(unittest.TestCase):
    def test_plain_text_only(self):
        result = text_to_textnodes("just plain text")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just plain text")
        self.assertEqual(result[0].text_type, TextType.PLAIN)

    def test_empty_string_returns_single_empty_plain_node(self):
        result = text_to_textnodes("")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "")
        self.assertEqual(result[0].text_type, TextType.PLAIN)

    def test_whitespace_only_stays_plain(self):
        result = text_to_textnodes("   ")
        self.assertEqual(result, [TextNode("   ", TextType.PLAIN)])


class TestTextToTextNodesSingleType(unittest.TestCase):
    def test_bold_only(self):
        result = text_to_textnodes("**bold**")
        self.assertEqual(result, [TextNode("bold", TextType.BOLD)])

    def test_italic_only(self):
        result = text_to_textnodes("_italic_")
        self.assertEqual(result, [TextNode("italic", TextType.ITALIC)])

    def test_code_only(self):
        result = text_to_textnodes("`code`")
        self.assertEqual(result, [TextNode("code", TextType.CODE)])

    def test_image_only(self):
        result = text_to_textnodes("![alt](url)")
        self.assertEqual(result, [TextNode("alt", TextType.IMAGE, "url")])

    def test_link_only(self):
        result = text_to_textnodes("[text](url)")
        self.assertEqual(result, [TextNode("text", TextType.LINK, "url")])


class TestTextToTextNodesFullPipeline(unittest.TestCase):
    def test_classic_reference_example(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Q4.jpeg) "
            "and a [link](https://boot.dev)"
        )
        result = text_to_textnodes(text)
        self.assertListEqual(
            result,
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.PLAIN),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.PLAIN),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Q4.jpeg"
                ),
                TextNode(" and a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )

    def test_bold_and_italic_together(self):
        result = text_to_textnodes("**bold** _italic_")
        self.assertEqual(texts(result), ["bold", " ", "italic"])
        self.assertEqual(
            types(result), [TextType.BOLD, TextType.PLAIN, TextType.ITALIC]
        )

    def test_multiple_of_each_type(self):
        result = text_to_textnodes("**a** **b** _c_ _d_ `e` `f`")
        self.assertEqual(
            texts(result), ["a", " ", "b", " ", "c", " ", "d", " ", "e", " ", "f"]
        )
        self.assertEqual(
            types(result),
            [
                TextType.BOLD,
                TextType.PLAIN,
                TextType.BOLD,
                TextType.PLAIN,
                TextType.ITALIC,
                TextType.PLAIN,
                TextType.ITALIC,
                TextType.PLAIN,
                TextType.CODE,
                TextType.PLAIN,
                TextType.CODE,
            ],
        )

    def test_image_and_link_together(self):
        result = text_to_textnodes("![img](u1) [link](u2)")
        self.assertEqual(texts(result), ["img", " ", "link"])
        self.assertEqual(types(result), [TextType.IMAGE, TextType.PLAIN, TextType.LINK])
        self.assertEqual(result[0].url, "u1")
        self.assertEqual(result[2].url, "u2")

    def test_output_order_follows_source_text_order(self):
        # Even though the pipeline processes one syntax type at a time
        # (code, then bold, then italic, then images, then links), the
        # final node list still reflects left-to-right reading order.
        result = text_to_textnodes("[link](u) **bold** `code` _em_ ![img](u2)")
        self.assertEqual(types(result)[0], TextType.LINK)
        self.assertEqual(types(result)[-1], TextType.IMAGE)
        # PLAIN separators between every styled segment
        self.assertEqual(types(result).count(TextType.PLAIN), 4)


class TestTextToTextNodesPipelineOrdering(unittest.TestCase):
    def test_bold_markers_inside_image_alt_text_now_preserved(self):
        # Images are extracted before the "**" pass runs, so markdown-like
        # characters in the alt text are now part of the image's text
        # rather than being split out first.
        result = text_to_textnodes("![**not bold**](url)")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "**not bold**")
        self.assertEqual(result[0].text_type, TextType.IMAGE)
        self.assertEqual(result[0].url, "url")

    def test_italic_markers_inside_link_text_now_preserved(self):
        result = text_to_textnodes("[_not italic_](url)")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "_not italic_")
        self.assertEqual(result[0].text_type, TextType.LINK)
        self.assertEqual(result[0].url, "url")

    def test_bold_text_containing_underscore_not_split_by_italic_pass(self):
        result = text_to_textnodes("**bold_word**")
        self.assertEqual(result, [TextNode("bold_word", TextType.BOLD)])

    def test_code_span_wrapping_image_syntax_raises(self):
        # The image is extracted from the PLAIN node first, stranding the
        # two backticks in separate fragments with an odd count each.
        with self.assertRaises(Exception):
            text_to_textnodes("`![alt](url)`")

    def test_code_span_wrapping_link_syntax_raises(self):
        with self.assertRaises(Exception):
            text_to_textnodes("`[text](url)`")

    def test_code_span_containing_bold_markers_still_protected(self):
        # Bold/italic delimiters run AFTER code, so this case is unaffected
        # by the reordering — code still protects its contents.
        result = text_to_textnodes("`**not bold**`")
        self.assertEqual(result, [TextNode("**not bold**", TextType.CODE)])

    def test_code_and_image_as_separate_non_overlapping_spans_both_work(self):
        # As long as the code span doesn't wrap the image/link syntax,
        # both are extracted correctly regardless of order.
        result = text_to_textnodes("`code` and ![img](u)")
        self.assertEqual(texts(result), ["code", " and ", "img"])
        self.assertEqual(types(result), [TextType.CODE, TextType.PLAIN, TextType.IMAGE])


class TestTextToTextNodesErrors(unittest.TestCase):
    def test_unclosed_bold_delimiter_raises(self):
        with self.assertRaises(Exception):
            text_to_textnodes("**unclosed")

    def test_unclosed_italic_delimiter_raises(self):
        with self.assertRaises(Exception):
            text_to_textnodes("_unclosed")

    def test_unclosed_code_delimiter_raises(self):
        with self.assertRaises(Exception):
            text_to_textnodes("`unclosed")

    def test_error_message_identifies_delimiter(self):
        with self.assertRaises(Exception) as ctx:
            text_to_textnodes("**unclosed")
        self.assertIn("**", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
