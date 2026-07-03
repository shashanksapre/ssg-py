import unittest

from markdown import BlockType, block_to_block_type, markdown_to_blocks


class TestBlockTypeHeading(unittest.TestCase):
    def test_h1(self):
        self.assertEqual(block_to_block_type("# Hello"), BlockType.HEADING)

    def test_h2(self):
        self.assertEqual(block_to_block_type("## Hello"), BlockType.HEADING)

    def test_h3(self):
        self.assertEqual(block_to_block_type("### Hello"), BlockType.HEADING)

    def test_h6_maximum(self):
        self.assertEqual(block_to_block_type("###### Hello"), BlockType.HEADING)

    def test_h7_too_many_hashes_is_paragraph(self):
        self.assertEqual(block_to_block_type("####### Hello"), BlockType.PARAGRAPH)

    def test_no_space_after_hashes_is_paragraph(self):
        # The regex requires at least one whitespace character after the hashes
        self.assertEqual(block_to_block_type("##NoSpace"), BlockType.PARAGRAPH)

    def test_lone_hashes_no_body_is_paragraph(self):
        self.assertEqual(block_to_block_type("######"), BlockType.PARAGRAPH)

    def test_lone_hash_is_paragraph(self):
        self.assertEqual(block_to_block_type("#"), BlockType.PARAGRAPH)

    def test_heading_with_empty_body_still_heading(self):
        # "# " — space satisfies \s, .* matches empty
        self.assertEqual(block_to_block_type("# "), BlockType.HEADING)

    def test_hash_not_at_start_is_paragraph(self):
        self.assertEqual(block_to_block_type("Not # a heading"), BlockType.PARAGRAPH)


class TestBlockTypeCode(unittest.TestCase):
    def test_basic_three_line_code_block(self):
        self.assertEqual(block_to_block_type("```\ncode here\n```"), BlockType.CODE)

    def test_four_line_code_block(self):
        self.assertEqual(block_to_block_type("```\nline1\nline2\n```"), BlockType.CODE)

    def test_code_with_language_hint_on_opening_fence(self):
        self.assertEqual(block_to_block_type("```python\ncode\n```"), BlockType.CODE)

    def test_closing_fence_with_trailing_text_still_code(self):
        # startswith("```") is true even if the closing line has extra chars
        self.assertEqual(block_to_block_type("```\ncode\n``` end"), BlockType.CODE)

    def test_two_lines_not_enough(self):
        # len(lines) < 3 → not CODE
        self.assertEqual(block_to_block_type("```\n```"), BlockType.PARAGRAPH)

    def test_single_line_both_fences_not_code(self):
        # Single-element list: first == last, but len < 3
        self.assertEqual(block_to_block_type("```code```"), BlockType.PARAGRAPH)

    def test_open_fence_but_no_close_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("```\ncode\nno close"), BlockType.PARAGRAPH
        )

    def test_close_fence_but_no_open_is_paragraph(self):
        self.assertEqual(block_to_block_type("start\ncode\n```"), BlockType.PARAGRAPH)


class TestBlockTypeQuote(unittest.TestCase):
    def test_single_quote_line(self):
        self.assertEqual(block_to_block_type("> quote"), BlockType.QUOTE)

    def test_multi_line_all_quoted(self):
        self.assertEqual(block_to_block_type("> a\n> b\n> c"), BlockType.QUOTE)

    def test_empty_quote_marker_only(self):
        # ">" with nothing after it still satisfies ^>.*
        self.assertEqual(block_to_block_type(">"), BlockType.QUOTE)

    def test_quote_marker_then_space(self):
        self.assertEqual(block_to_block_type("> "), BlockType.QUOTE)

    def test_multi_line_empty_markers(self):
        self.assertEqual(block_to_block_type(">\n>\n>"), BlockType.QUOTE)

    def test_one_non_quote_line_is_paragraph(self):
        self.assertEqual(
            block_to_block_type("> a\nnot quote\n> b"), BlockType.PARAGRAPH
        )

    def test_first_line_not_quote_is_paragraph(self):
        self.assertEqual(block_to_block_type("no quote\n> b"), BlockType.PARAGRAPH)


class TestBlockTypeUnorderedList(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDERED_LIST)

    def test_multiple_items(self):
        self.assertEqual(block_to_block_type("- a\n- b\n- c"), BlockType.UNORDERED_LIST)

    def test_items_with_trailing_spaces(self):
        self.assertEqual(
            block_to_block_type("- item   \n- item2"), BlockType.UNORDERED_LIST
        )

    def test_dash_without_space_is_paragraph(self):
        # "-item" — no whitespace after the dash
        self.assertEqual(block_to_block_type("-item"), BlockType.PARAGRAPH)

    def test_mixed_ul_and_plain_is_paragraph(self):
        self.assertEqual(block_to_block_type("- a\nplain\n- b"), BlockType.PARAGRAPH)

    def test_ul_then_non_ul_line_at_end_is_paragraph(self):
        self.assertEqual(block_to_block_type("- a\n- b\nno dash"), BlockType.PARAGRAPH)

    def test_first_line_not_ul_is_paragraph(self):
        self.assertEqual(block_to_block_type("plain\n- b"), BlockType.PARAGRAPH)


class TestBlockTypeOrderedList(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(block_to_block_type("1. item"), BlockType.ORDERED_LIST)

    def test_three_items_sequential(self):
        self.assertEqual(
            block_to_block_type("1. a\n2. b\n3. c"), BlockType.ORDERED_LIST
        )

    def test_five_items_sequential(self):
        self.assertEqual(
            block_to_block_type("1. a\n2. b\n3. c\n4. d\n5. e"), BlockType.ORDERED_LIST
        )

    def test_starts_at_two_not_one_is_paragraph(self):
        # Must start at 1; "^1\.\s.*" won't match "2. ..."
        self.assertEqual(block_to_block_type("2. a\n3. b"), BlockType.PARAGRAPH)

    def test_skips_a_number_is_paragraph(self):
        self.assertEqual(block_to_block_type("1. a\n3. b"), BlockType.PARAGRAPH)

    def test_descending_order_is_paragraph(self):
        self.assertEqual(block_to_block_type("3. a\n2. b\n1. c"), BlockType.PARAGRAPH)

    def test_gap_later_in_sequence_is_paragraph(self):
        self.assertEqual(block_to_block_type("1. a\n2. b\n4. d"), BlockType.PARAGRAPH)

    def test_no_space_after_period_is_paragraph(self):
        self.assertEqual(block_to_block_type("1.item"), BlockType.PARAGRAPH)

    def test_first_line_matches_but_second_does_not_is_paragraph(self):
        self.assertEqual(block_to_block_type("1. a\nnot numbered"), BlockType.PARAGRAPH)


class TestBlockTypeParagraph(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(block_to_block_type("Just some text"), BlockType.PARAGRAPH)

    def test_multi_line_plain_text(self):
        self.assertEqual(block_to_block_type("Line one\nLine two"), BlockType.PARAGRAPH)

    def test_inline_markdown_is_still_paragraph(self):
        # Block type is structural; inline markers don't change the block type
        self.assertEqual(
            block_to_block_type("This is **bold** and _italic_ text"),
            BlockType.PARAGRAPH,
        )

    def test_returns_block_type_enum_instance(self):
        result = block_to_block_type("plain")
        self.assertIsInstance(result, BlockType)


class TestBlockTypeIntegration(unittest.TestCase):
    def test_full_document_types_in_order(self):
        md = (
            "# My Title\n\n"
            "A paragraph of text.\n\n"
            "```\nsome code\nmore code\n```\n\n"
            "> a quote\n\n"
            "- item one\n- item two\n\n"
            "1. first\n2. second\n3. third"
        )
        blocks = markdown_to_blocks(md)
        types = [block_to_block_type(b) for b in blocks]
        self.assertEqual(
            types,
            [
                BlockType.HEADING,
                BlockType.PARAGRAPH,
                BlockType.CODE,
                BlockType.QUOTE,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
            ],
        )

    def test_every_block_type_value_is_reachable(self):
        samples = {
            BlockType.HEADING: "# title",
            BlockType.CODE: "```\ncode\n```",
            BlockType.QUOTE: "> quote",
            BlockType.UNORDERED_LIST: "- item",
            BlockType.ORDERED_LIST: "1. item",
            BlockType.PARAGRAPH: "plain text",
        }
        for expected, block in samples.items():
            with self.subTest(block_type=expected.name):
                self.assertEqual(block_to_block_type(block), expected)


if __name__ == "__main__":
    unittest.main()
