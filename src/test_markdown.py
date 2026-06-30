import unittest

from markdown import markdown_to_blocks


class TestMarkdownToBlocksEmpty(unittest.TestCase):
    def test_empty_string_returns_empty_list(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_whitespace_only_returns_empty_list(self):
        self.assertEqual(markdown_to_blocks("   \n\n   "), [])

    def test_only_blank_lines_returns_empty_list(self):
        self.assertEqual(markdown_to_blocks("\n\n\n\n"), [])

    def test_single_newline_returns_empty_list(self):
        # No "\n\n" separator present, but strip() reduces it to ""
        self.assertEqual(markdown_to_blocks("\n"), [])


class TestMarkdownToBlocksSingleBlock(unittest.TestCase):
    def test_single_paragraph(self):
        self.assertEqual(
            markdown_to_blocks("Just one paragraph"), ["Just one paragraph"]
        )

    def test_single_paragraph_strips_surrounding_whitespace(self):
        self.assertEqual(
            markdown_to_blocks("   Just one paragraph   "), ["Just one paragraph"]
        )

    def test_single_paragraph_strips_surrounding_newlines(self):
        self.assertEqual(
            markdown_to_blocks("\n\nJust one paragraph\n\n"), ["Just one paragraph"]
        )

    def test_multiline_block_without_blank_line_stays_one_block(self):
        # A single "\n" is not a block separator — only "\n\n" is
        result = markdown_to_blocks("Para line1\nPara line2")
        self.assertEqual(result, ["Para line1\nPara line2"])


class TestMarkdownToBlocksMultipleBlocks(unittest.TestCase):
    def test_two_blocks(self):
        result = markdown_to_blocks("First paragraph\n\nSecond paragraph")
        self.assertEqual(result, ["First paragraph", "Second paragraph"])

    def test_three_blocks(self):
        result = markdown_to_blocks("First\n\nSecond\n\nThird")
        self.assertEqual(result, ["First", "Second", "Third"])

    def test_blocks_preserve_source_order(self):
        result = markdown_to_blocks("Z\n\nA\n\nM")
        self.assertEqual(result, ["Z", "A", "M"])

    def test_heading_and_paragraph(self):
        result = markdown_to_blocks("# Heading\n\nParagraph text")
        self.assertEqual(result, ["# Heading", "Paragraph text"])

    def test_list_block_kept_as_single_multiline_block(self):
        result = markdown_to_blocks("- item1\n- item2\n\nNext paragraph")
        self.assertEqual(result, ["- item1\n- item2", "Next paragraph"])


class TestMarkdownToBlocksInternalWhitespace(unittest.TestCase):
    def test_internal_line_indentation_preserved(self):
        # Only the block's outer whitespace is stripped; internal
        # indentation on inner lines is left untouched.
        result = markdown_to_blocks("Line one\n  Line two indented\n\nNext block")
        self.assertEqual(result, ["Line one\n  Line two indented", "Next block"])

    def test_trailing_newline_after_single_block_stripped(self):
        self.assertEqual(markdown_to_blocks("Some text\n"), ["Some text"])


class TestMarkdownToBlocksExcessSeparators(unittest.TestCase):
    def test_extra_blank_line_between_blocks_does_not_create_empty_block(self):
        # "A\n\n\n\nB" splits on "\n\n" into ["A", "", "B"]; the empty
        # middle entry must be dropped, not kept as an empty string.
        result = markdown_to_blocks("A\n\n\n\nB")
        self.assertEqual(result, ["A", "B"])

    def test_whitespace_only_block_between_real_blocks_dropped(self):
        result = markdown_to_blocks("First\n\n   \n\nSecond")
        self.assertEqual(result, ["First", "Second"])

    def test_tabs_only_block_between_real_blocks_dropped(self):
        result = markdown_to_blocks("A\n\n\t\t\n\nB")
        self.assertEqual(result, ["A", "B"])

    def test_leading_and_trailing_blank_blocks_dropped(self):
        result = markdown_to_blocks("\n\nFirst\n\nSecond\n\n")
        self.assertEqual(result, ["First", "Second"])

    def test_no_empty_strings_anywhere_in_result(self):
        result = markdown_to_blocks("A\n\n\n\nB\n\n   \n\nC")
        self.assertNotIn("", result)
        self.assertEqual(result, ["A", "B", "C"])


class TestMarkdownToBlocksReferenceExample(unittest.TestCase):
    def test_mixed_content_document(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\n"
                "This is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_returns_a_list_of_strings(self):
        result = markdown_to_blocks("A\n\nB")
        self.assertIsInstance(result, list)
        for block in result:
            self.assertIsInstance(block, str)


if __name__ == "__main__":
    unittest.main()
