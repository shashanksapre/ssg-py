import unittest

from markdown import markdown_to_html_node, extract_title


def html(md: str) -> str:
    return markdown_to_html_node(md).to_html()


class TestMarkdownToHTMLNodeWrapper(unittest.TestCase):
    def test_root_tag_is_div(self):
        node = markdown_to_html_node("plain text")
        self.assertEqual(node.tag, "div")

    def test_single_block_wrapped_in_div(self):
        result = html("plain")
        self.assertTrue(result.startswith("<div>"))
        self.assertTrue(result.endswith("</div>"))

    def test_multiple_blocks_all_inside_one_div(self):
        result = html("First\n\nSecond")
        self.assertEqual(result.count("<div>"), 1)
        self.assertEqual(result.count("</div>"), 1)


class TestMarkdownToHTMLNodeParagraph(unittest.TestCase):
    def test_plain_paragraph(self):
        self.assertEqual(html("plain text"), "<div><p>plain text</p></div>")

    def test_multiline_paragraph_lines_joined_with_space(self):
        self.assertEqual(
            html("line one\nline two"), "<div><p>line one line two</p></div>"
        )

    def test_three_line_paragraph_joined(self):
        self.assertEqual(html("one\ntwo\nthree"), "<div><p>one two three</p></div>")

    def test_paragraph_with_bold_inline(self):
        self.assertEqual(html("**bold** text"), "<div><p><b>bold</b> text</p></div>")

    def test_paragraph_with_italic_inline(self):
        self.assertEqual(html("_italic_ text"), "<div><p><i>italic</i> text</p></div>")

    def test_paragraph_with_code_inline(self):
        self.assertEqual(html("`code`"), "<div><p><code>code</code></p></div>")

    def test_two_paragraphs(self):
        self.assertEqual(
            html("First paragraph\n\nSecond paragraph"),
            "<div><p>First paragraph</p><p>Second paragraph</p></div>",
        )

    def test_existing_paragraphs_test(self):
        md = (
            "This is **bolded** paragraph\n"
            "text in a p\n"
            "tag here\n\n"
            "This is another paragraph with _italic_ text and `code` here"
        )
        self.assertEqual(
            html(md),
            "<div>"
            "<p>This is <b>bolded</b> paragraph text in a p tag here</p>"
            "<p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p>"
            "</div>",
        )


class TestMarkdownToHTMLNodeHeading(unittest.TestCase):
    def test_h1(self):
        self.assertEqual(html("# Title"), "<div><h1>Title</h1></div>")

    def test_h2(self):
        self.assertEqual(html("## Title"), "<div><h2>Title</h2></div>")

    def test_h3(self):
        self.assertEqual(html("### Title"), "<div><h3>Title</h3></div>")

    def test_h4(self):
        self.assertEqual(html("#### Title"), "<div><h4>Title</h4></div>")

    def test_h5(self):
        self.assertEqual(html("##### Title"), "<div><h5>Title</h5></div>")

    def test_h6(self):
        self.assertEqual(html("###### Title"), "<div><h6>Title</h6></div>")

    def test_heading_with_multi_word_title(self):
        self.assertEqual(html("### Hello World"), "<div><h3>Hello World</h3></div>")

    def test_heading_with_bold_inline(self):
        self.assertEqual(
            html("# **bold** title"), "<div><h1><b>bold</b> title</h1></div>"
        )

    def test_heading_with_italic_inline(self):
        self.assertEqual(
            html("## _italic_ title"), "<div><h2><i>italic</i> title</h2></div>"
        )


class TestMarkdownToHTMLNodeCode(unittest.TestCase):
    def test_basic_code_block_wrapped_in_pre_and_code(self):
        self.assertEqual(
            html("```\nsome code\n```"),
            "<div><pre><code>some code\n</code></pre></div>",
        )

    def test_multiline_code_content_preserved(self):
        self.assertEqual(
            html("```\nline1\nline2\nline3\n```"),
            "<div><pre><code>line1\nline2\nline3\n</code></pre></div>",
        )

    def test_code_block_trailing_newline_included_in_content(self):
        # block[4:-3] preserves the \n before the closing fence
        result = html("```\ncontent\n```")
        self.assertIn("content\n", result)

    def test_inline_markdown_inside_code_block_not_processed(self):
        # The code handler uses LeafNode directly, not text_to_textnodes,
        # so ** and _ inside a code block must appear verbatim in the output.
        self.assertEqual(
            html("```\n_should_ remain\nthe **same**\n```"),
            "<div><pre><code>_should_ remain\nthe **same**\n</code></pre></div>",
        )

    def test_code_block_with_language_hint_slices_incorrectly(self):
        # block[4:-3] always skips exactly 4 characters from the start.
        # Opening fence "```python" is 9 chars, so [4:-3] starts inside
        # the language name rather than at the first line of code content.
        # This is a known limitation: "ython\n" leaks into the output.
        result = html("```python\nsome code\n```")
        self.assertIn("ython", result)
        self.assertNotIn("<code>some code", result)

    def test_existing_codeblock_test(self):
        md = "```\nThis is text that _should_ remain\nthe **same** even with inline stuff\n```"
        self.assertEqual(
            html(md),
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


class TestMarkdownToHTMLNodeQuote(unittest.TestCase):
    def test_single_line_quote(self):
        self.assertEqual(
            html("> simple quote"),
            "<div><blockquote>simple quote</blockquote></div>",
        )

    def test_quote_marker_stripped(self):
        # "> text" → stripped to "text"; the ">" marker must not appear
        # in the blockquote content (note: "</blockquote>" contains ">" but
        # that is the closing HTML tag, not a leaked markdown marker)
        result = html("> text")
        self.assertIn("<blockquote>text</blockquote>", result)
        self.assertNotIn("&gt;", result)

    def test_quote_no_space_after_marker_also_stripped(self):
        self.assertEqual(
            html(">no space"),
            "<div><blockquote>no space</blockquote></div>",
        )

    def test_multiline_quote_lines_joined_with_space(self):
        self.assertEqual(
            html("> line one\n> line two"),
            "<div><blockquote>line one line two</blockquote></div>",
        )

    def test_three_line_quote(self):
        self.assertEqual(
            html("> a\n> b\n> c"),
            "<div><blockquote>a b c</blockquote></div>",
        )

    def test_quote_with_bold_inline(self):
        self.assertEqual(
            html("> **bold** quote"),
            "<div><blockquote><b>bold</b> quote</blockquote></div>",
        )

    def test_quote_with_code_inline(self):
        self.assertEqual(
            html("> A quote with `code`"),
            "<div><blockquote>A quote with <code>code</code></blockquote></div>",
        )


class TestMarkdownToHTMLNodeUnorderedList(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(
            html("- item one"),
            "<div><ul><li>item one</li></ul></div>",
        )

    def test_multiple_items(self):
        self.assertEqual(
            html("- item one\n- item two\n- item three"),
            "<div><ul><li>item one</li><li>item two</li><li>item three</li></ul></div>",
        )

    def test_item_count_matches(self):
        result = html("- a\n- b\n- c")
        self.assertEqual(result.count("<li>"), 3)
        self.assertEqual(result.count("</li>"), 3)

    def test_items_wrapped_in_ul(self):
        result = html("- item")
        self.assertIn("<ul>", result)
        self.assertIn("</ul>", result)

    def test_item_with_bold_inline(self):
        self.assertEqual(
            html("- **bold** item"),
            "<div><ul><li><b>bold</b> item</li></ul></div>",
        )

    def test_item_with_italic_inline(self):
        self.assertEqual(
            html("- _italic_ item"),
            "<div><ul><li><i>italic</i> item</li></ul></div>",
        )

    def test_mixed_inline_items(self):
        self.assertEqual(
            html("- **bold** item\n- _italic_ item"),
            "<div><ul><li><b>bold</b> item</li><li><i>italic</i> item</li></ul></div>",
        )

    def test_item_containing_period_not_broken_by_ol_split(self):
        # line.split("- ", 1)[1] is used, not ". ", so periods in UL items are safe
        self.assertEqual(
            html("- item with 1. inside"),
            "<div><ul><li>item with 1. inside</li></ul></div>",
        )


class TestMarkdownToHTMLNodeOrderedList(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(
            html("1. first"),
            "<div><ol><li>first</li></ol></div>",
        )

    def test_multiple_items(self):
        self.assertEqual(
            html("1. first\n2. second\n3. third"),
            "<div><ol><li>first</li><li>second</li><li>third</li></ol></div>",
        )

    def test_item_count_matches(self):
        result = html("1. a\n2. b\n3. c")
        self.assertEqual(result.count("<li>"), 3)

    def test_items_wrapped_in_ol(self):
        result = html("1. item")
        self.assertIn("<ol>", result)
        self.assertIn("</ol>", result)

    def test_item_with_bold_inline(self):
        self.assertEqual(
            html("1. **bold** item\n2. normal"),
            "<div><ol><li><b>bold</b> item</li><li>normal</li></ol></div>",
        )

    def test_item_containing_dash_not_broken_by_ul_split(self):
        # line.split(". ", 1)[1] is used, so a dash in the item text is safe
        self.assertEqual(
            html("1. item - with dash"),
            "<div><ol><li>item - with dash</li></ol></div>",
        )

    def test_number_prefix_stripped_from_each_item(self):
        result = html("1. first\n2. second")
        self.assertNotIn("1.", result)
        self.assertNotIn("2.", result)


class TestMarkdownToHTMLNodeFullDocument(unittest.TestCase):
    def test_all_six_block_types_in_one_document(self):
        md = (
            "# Heading\n\n"
            "Paragraph text.\n\n"
            "```\ncode\n```\n\n"
            "> quote\n\n"
            "- ul\n\n"
            "1. ol"
        )
        self.assertEqual(
            html(md),
            "<div>"
            "<h1>Heading</h1>"
            "<p>Paragraph text.</p>"
            "<pre><code>code\n</code></pre>"
            "<blockquote>quote</blockquote>"
            "<ul><li>ul</li></ul>"
            "<ol><li>ol</li></ol>"
            "</div>",
        )

    def test_block_order_preserved(self):
        md = "# First\n\nSecond paragraph\n\n> Third quote"
        result = html(md)
        h1_pos = result.index("<h1>")
        p_pos = result.index("<p>")
        bq_pos = result.index("<blockquote>")
        self.assertLess(h1_pos, p_pos)
        self.assertLess(p_pos, bq_pos)

    def test_heading_then_list(self):
        md = "## Shopping List\n\n- apples\n- bananas"
        self.assertEqual(
            html(md),
            "<div><h2>Shopping List</h2><ul><li>apples</li><li>bananas</li></ul></div>",
        )


class TestExtractTitleReturnsTitle(unittest.TestCase):
    def test_simple_h1(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_multi_word_title(self):
        self.assertEqual(extract_title("# Hello World"), "Hello World")

    def test_h1_before_paragraph(self):
        self.assertEqual(extract_title("# Title\n\nSome paragraph"), "Title")

    def test_h1_after_paragraph(self):
        self.assertEqual(extract_title("Intro paragraph\n\n# Title"), "Title")

    def test_h1_in_middle_of_document(self):
        self.assertEqual(
            extract_title("Intro\n\n# Middle Title\n\nOutro"), "Middle Title"
        )

    def test_first_h1_returned_when_multiple_present(self):
        self.assertEqual(extract_title("# First\n\n# Second"), "First")

    def test_title_containing_hash_after_space(self):
        # split("# ", 1)[1] returns everything after the first "# "
        self.assertEqual(extract_title("# Hello # World"), "Hello # World")

    def test_h1_preceded_by_h2_block(self):
        self.assertEqual(extract_title("## Section\n\n# Real Title"), "Real Title")

    def test_h1_with_inline_bold_returned_verbatim(self):
        # extract_title returns the raw text; inline markdown is not processed
        self.assertEqual(extract_title("# **bold** title"), "**bold** title")

    def test_h1_with_inline_italic_returned_verbatim(self):
        self.assertEqual(extract_title("# Title with _italic_"), "Title with _italic_")

    def test_surrounding_blank_lines_stripped_by_blocks(self):
        self.assertEqual(extract_title("\n\n# Title\n\n"), "Title")


class TestExtractTitleRaises(unittest.TestCase):
    def test_no_heading_raises(self):
        with self.assertRaises(Exception):
            extract_title("No heading here")

    def test_empty_string_raises(self):
        with self.assertRaises(Exception):
            extract_title("")

    def test_whitespace_only_raises(self):
        with self.assertRaises(Exception):
            extract_title("   \n\n   ")

    def test_h2_only_raises(self):
        # "##" does not startswith("# "), so h2+ are not treated as titles
        with self.assertRaises(Exception):
            extract_title("## Not a title")

    def test_h3_only_raises(self):
        with self.assertRaises(Exception):
            extract_title("### Also not a title")

    def test_hash_not_at_block_start_raises(self):
        # A "# " appearing mid-paragraph is not a heading block
        with self.assertRaises(Exception):
            extract_title("This paragraph mentions # hash but has no h1")

    def test_exception_message_is_descriptive(self):
        with self.assertRaises(Exception) as ctx:
            extract_title("No heading")
        self.assertIn("Heading", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
