import unittest

from helpers import extract_markdown_images, extract_markdown_links


class TestExtractImagesNoMatch(unittest.TestCase):
    def test_no_markdown_returns_empty_list(self):
        self.assertEqual(extract_markdown_images("no markdown here"), [])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(extract_markdown_images(""), [])

    def test_plain_link_is_not_an_image(self):
        self.assertEqual(extract_markdown_images("[a link](https://example.com)"), [])

    def test_lone_exclamation_mark_not_matched(self):
        self.assertEqual(extract_markdown_images("text with ! but not markdown"), [])

    def test_double_exclamation_without_brackets_not_matched(self):
        self.assertEqual(extract_markdown_images("text with !!not an image marker"), [])

    def test_nested_brackets_in_alt_text_not_matched(self):
        # The character class [^\[\]]* stops at the first inner "[",
        # so unbalanced/nested brackets break the match entirely.
        self.assertEqual(extract_markdown_images("![not v[alid]](url)"), [])

    def test_parens_inside_url_breaks_match(self):
        # [^\(\)]* stops at the first inner "(", so a literal paren
        # inside the URL prevents the whole pattern from matching.
        self.assertEqual(
            extract_markdown_images("![alt](url with (parens) inside)"), []
        )


class TestExtractImagesSingleMatch(unittest.TestCase):
    def test_basic_image(self):
        result = extract_markdown_images("![alt text](https://example.com/img.png)")
        self.assertEqual(result, [("alt text", "https://example.com/img.png")])

    def test_image_surrounded_by_text(self):
        result = extract_markdown_images("text before ![alt](url.png) text after")
        self.assertEqual(result, [("alt", "url.png")])

    def test_empty_url(self):
        result = extract_markdown_images("![alt]() empty url")
        self.assertEqual(result, [("alt", "")])

    def test_empty_alt_text(self):
        result = extract_markdown_images("![](url.png) empty alt")
        self.assertEqual(result, [("", "url.png")])

    def test_both_alt_and_url_empty(self):
        self.assertEqual(extract_markdown_images("![]()"), [("", "")])

    def test_alt_text_with_spaces_and_punctuation(self):
        result = extract_markdown_images("![only image, no link]()")
        self.assertEqual(result, [("only image, no link", "")])

    def test_url_with_spaces(self):
        result = extract_markdown_images(
            "![alt text with spaces](https://example.com/path with spaces.png)"
        )
        self.assertEqual(
            result,
            [("alt text with spaces", "https://example.com/path with spaces.png")],
        )

    def test_url_with_query_string(self):
        result = extract_markdown_images("![alt](url?query=1&other=2)")
        self.assertEqual(result, [("alt", "url?query=1&other=2")])

    def test_image_across_newlines_in_surrounding_text(self):
        result = extract_markdown_images("multiline text\n![alt](url.png)\nmore text")
        self.assertEqual(result, [("alt", "url.png")])

    def test_returns_list_of_tuples(self):
        result = extract_markdown_images("![alt](url.png)")
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], tuple)
        self.assertEqual(len(result[0]), 2)


class TestExtractImagesMultipleMatches(unittest.TestCase):
    def test_two_images(self):
        result = extract_markdown_images("![img1](url1.png) and ![img2](url2.png)")
        self.assertEqual(result, [("img1", "url1.png"), ("img2", "url2.png")])

    def test_four_images_in_order(self):
        result = extract_markdown_images("![a](b) ![c](d) ![e](f) ![g](h)")
        self.assertEqual(result, [("a", "b"), ("c", "d"), ("e", "f"), ("g", "h")])

    def test_image_count_matches_occurrences(self):
        result = extract_markdown_images("![a](b) ![c](d) ![e](f)")
        self.assertEqual(len(result), 3)


class TestExtractImagesIgnoresLinks(unittest.TestCase):
    def test_image_and_link_together_only_image_extracted(self):
        text = "mix ![image](img.png) and [link](page.html) together"
        self.assertEqual(extract_markdown_images(text), [("image", "img.png")])

    def test_link_then_image_only_image_extracted(self):
        text = "[link](url) followed by ![image](url2)"
        self.assertEqual(extract_markdown_images(text), [("image", "url2")])

    def test_multiple_links_and_one_image(self):
        text = "[link](url) ![image](url2) [link2](url3)"
        self.assertEqual(extract_markdown_images(text), [("image", "url2")])

    def test_image_marker_distinguishes_alt_text_containing_link_word(self):
        text = "not an image [but a link](url) and not a link ![but an image](url2)"
        self.assertEqual(extract_markdown_images(text), [("but an image", "url2")])


class TestExtractLinksNoMatch(unittest.TestCase):
    def test_no_markdown_returns_empty_list(self):
        self.assertEqual(extract_markdown_links("no markdown here"), [])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(extract_markdown_links(""), [])

    def test_image_is_not_a_link(self):
        self.assertEqual(
            extract_markdown_links("![alt text](https://example.com/img.png)"), []
        )

    def test_nested_brackets_in_link_text_not_matched(self):
        self.assertEqual(extract_markdown_links("[not v[alid]](url)"), [])

    def test_parens_inside_url_breaks_match(self):
        self.assertEqual(extract_markdown_links("[text](url with (parens) inside)"), [])


class TestExtractLinksSingleMatch(unittest.TestCase):
    def test_basic_link(self):
        result = extract_markdown_links("[a link](https://example.com)")
        self.assertEqual(result, [("a link", "https://example.com")])

    def test_link_surrounded_by_text(self):
        result = extract_markdown_links("text [link](https://example.com) more text")
        self.assertEqual(result, [("link", "https://example.com")])

    def test_empty_url(self):
        result = extract_markdown_links("[link]()")
        self.assertEqual(result, [("link", "")])

    def test_empty_link_text(self):
        result = extract_markdown_links("[](url.html)")
        self.assertEqual(result, [("", "url.html")])

    def test_both_text_and_url_empty(self):
        result = extract_markdown_links("[]() both empty")
        self.assertEqual(result, [("", "")])

    def test_returns_list_of_tuples(self):
        result = extract_markdown_links("[link](url)")
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], tuple)
        self.assertEqual(len(result[0]), 2)


class TestExtractLinksMultipleMatches(unittest.TestCase):
    def test_two_links(self):
        result = extract_markdown_links("[link1](url1) and [link2](url2)")
        self.assertEqual(result, [("link1", "url1"), ("link2", "url2")])

    def test_link_count_matches_occurrences(self):
        result = extract_markdown_links("[a](b) [c](d) [e](f)")
        self.assertEqual(len(result), 3)


class TestExtractLinksIgnoresImages(unittest.TestCase):
    def test_image_and_link_together_only_link_extracted(self):
        text = "mix ![image](img.png) and [link](page.html) together"
        self.assertEqual(extract_markdown_links(text), [("link", "page.html")])

    def test_image_preceding_link_does_not_consume_bracket(self):
        # The negative lookbehind (?<!!) must reject the "[" that is
        # immediately preceded by "!", without also rejecting a
        # legitimate link elsewhere in the same string.
        text = "![image](img.png) and [link](page.html)"
        self.assertEqual(extract_markdown_links(text), [("link", "page.html")])

    def test_link_then_image_only_link_extracted(self):
        text = "[link](url) followed by ![image](url2)"
        self.assertEqual(extract_markdown_links(text), [("link", "url")])

    def test_space_before_bang_does_not_block_lookbehind(self):
        # A "!" earlier in the string (not directly before "[") must not
        # cause the link to be skipped.
        text = "trailing ! before bracket but space ! [link](url)"
        self.assertEqual(extract_markdown_links(text), [("link", "url")])

    def test_three_mixed_nodes_correct_split(self):
        text = "[link](url) ![image](url2) [link2](url3)"
        self.assertEqual(
            extract_markdown_links(text), [("link", "url"), ("link2", "url3")]
        )


if __name__ == "__main__":
    unittest.main()
