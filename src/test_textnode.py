import unittest

from textnode import TextNode, TextType, split_nodes_image, split_nodes_link


def types(nodes: list[TextNode]) -> list[TextType]:
    return [n.text_type for n in nodes]


def texts(nodes: list[TextNode]) -> list[str]:
    return [n.text for n in nodes]


class TestSplitImagePassthrough(unittest.TestCase):
    def test_empty_list_returns_empty(self):
        self.assertEqual(split_nodes_image([]), [])

    def test_plain_node_with_no_image_unchanged(self):
        node = TextNode("just plain text", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just plain text")
        self.assertEqual(result[0].text_type, TextType.PLAIN)

    def test_plain_node_empty_text_unchanged(self):
        node = TextNode("", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "")

    def test_plain_node_containing_only_a_link_unchanged(self):
        # extract_markdown_images requires the "!" prefix, so a node
        # containing only link syntax (no images) must pass through whole.
        node = TextNode("a [link](url) only", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "a [link](url) only")
        self.assertEqual(result[0].text_type, TextType.PLAIN)

    def test_bold_node_passes_through(self):
        node = TextNode("![looks like an image](url)", TextType.BOLD)
        result = split_nodes_image([node])
        self.assertEqual(result, [node])

    def test_italic_node_passes_through(self):
        node = TextNode("![also looks like one](url)", TextType.ITALIC)
        result = split_nodes_image([node])
        self.assertEqual(result, [node])

    def test_image_node_passes_through_unchanged(self):
        node = TextNode("cat", TextType.IMAGE, "/cat.png")
        result = split_nodes_image([node])
        self.assertEqual(result, [node])


class TestSplitImageBasic(unittest.TestCase):
    def test_image_in_middle(self):
        node = TextNode("some text ![image](url.png) more text", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(texts(result), ["some text ", "image", " more text"])
        self.assertEqual(
            types(result), [TextType.PLAIN, TextType.IMAGE, TextType.PLAIN]
        )

    def test_image_at_start(self):
        node = TextNode("![image](url.png) and more text", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(texts(result), ["image", " and more text"])
        self.assertEqual(types(result), [TextType.IMAGE, TextType.PLAIN])

    def test_image_at_end(self):
        node = TextNode("some text ![image](url.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(texts(result), ["some text ", "image"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.IMAGE])

    def test_image_only_no_surrounding_text(self):
        node = TextNode("![image](url.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "image")
        self.assertEqual(result[0].text_type, TextType.IMAGE)
        self.assertEqual(result[0].url, "url.png")

    def test_image_node_url_preserved(self):
        node = TextNode("![alt](https://example.com/a.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(result[0].url, "https://example.com/a.png")


class TestSplitImageMultiple(unittest.TestCase):
    def test_two_images_with_reference_example(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) "
            "and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_three_images_back_to_back_with_separators(self):
        node = TextNode("![a](1) ![b](2) ![c](3)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(texts(result), ["a", " ", "b", " ", "c"])
        self.assertEqual(
            types(result),
            [
                TextType.IMAGE,
                TextType.PLAIN,
                TextType.IMAGE,
                TextType.PLAIN,
                TextType.IMAGE,
            ],
        )

    def test_duplicate_image_markdown_both_extracted(self):
        # Each occurrence is split off individually via str.split(..., 1),
        # so identical alt/url pairs appearing twice both get extracted.
        node = TextNode("![dup](u) text ![dup](u) more", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(texts(result), ["dup", " text ", "dup", " more"])
        self.assertEqual(
            types(result),
            [TextType.IMAGE, TextType.PLAIN, TextType.IMAGE, TextType.PLAIN],
        )


class TestSplitImageMixedList(unittest.TestCase):
    def test_plain_image_nodes_interleaved_with_other_types(self):
        nodes = [
            TextNode("first ![a](u1) node", TextType.PLAIN),
            TextNode("already bold", TextType.BOLD),
            TextNode("second ![b](u2) node", TextType.PLAIN),
        ]
        result = split_nodes_image(nodes)
        self.assertEqual(
            texts(result),
            ["first ", "a", " node", "already bold", "second ", "b", " node"],
        )
        self.assertEqual(
            types(result),
            [
                TextType.PLAIN,
                TextType.IMAGE,
                TextType.PLAIN,
                TextType.BOLD,
                TextType.PLAIN,
                TextType.IMAGE,
                TextType.PLAIN,
            ],
        )

    def test_output_order_matches_input_order(self):
        nodes = [
            TextNode("![first](u1)", TextType.PLAIN),
            TextNode("![second](u2)", TextType.PLAIN),
        ]
        result = split_nodes_image(nodes)
        self.assertEqual(texts(result), ["first", "second"])


class TestSplitLinkPassthrough(unittest.TestCase):
    def test_empty_list_returns_empty(self):
        self.assertEqual(split_nodes_link([]), [])

    def test_plain_node_with_no_link_unchanged(self):
        node = TextNode("just plain text", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just plain text")
        self.assertEqual(result[0].text_type, TextType.PLAIN)

    def test_plain_node_empty_text_unchanged(self):
        node = TextNode("", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "")

    def test_bold_node_passes_through(self):
        node = TextNode("[looks like a link](url)", TextType.BOLD)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_image_node_passes_through(self):
        node = TextNode("[looks like a link too](url)", TextType.IMAGE, "u")
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_link_node_passes_through_unchanged(self):
        node = TextNode("Google", TextType.LINK, "https://google.com")
        result = split_nodes_link([node])
        self.assertEqual(result, [node])


class TestSplitLinkBasic(unittest.TestCase):
    def test_link_in_middle(self):
        node = TextNode("some text [link](url.com) more text", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(texts(result), ["some text ", "link", " more text"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.LINK, TextType.PLAIN])

    def test_link_at_start(self):
        node = TextNode("[link](url.com) and more text", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(texts(result), ["link", " and more text"])
        self.assertEqual(types(result), [TextType.LINK, TextType.PLAIN])

    def test_link_at_end(self):
        node = TextNode("some text [link](url.com)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(texts(result), ["some text ", "link"])
        self.assertEqual(types(result), [TextType.PLAIN, TextType.LINK])

    def test_link_only_no_surrounding_text(self):
        node = TextNode("[link](url.com)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "link")
        self.assertEqual(result[0].text_type, TextType.LINK)
        self.assertEqual(result[0].url, "url.com")

    def test_link_node_url_preserved(self):
        node = TextNode("[click](https://example.com/page)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result[0].url, "https://example.com/page")


class TestSplitLinkMultiple(unittest.TestCase):
    def test_two_links_with_reference_example(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and another "
            "[second link](https://example.com/2)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode("second link", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_three_links_back_to_back_with_separators(self):
        node = TextNode("[a](1) [b](2) [c](3)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(texts(result), ["a", " ", "b", " ", "c"])
        self.assertEqual(
            types(result),
            [
                TextType.LINK,
                TextType.PLAIN,
                TextType.LINK,
                TextType.PLAIN,
                TextType.LINK,
            ],
        )

    def test_duplicate_link_markdown_both_extracted(self):
        node = TextNode("[dup](u) text [dup](u) more", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(texts(result), ["dup", " text ", "dup", " more"])
        self.assertEqual(
            types(result),
            [TextType.LINK, TextType.PLAIN, TextType.LINK, TextType.PLAIN],
        )


class TestSplitLinkMixedList(unittest.TestCase):
    def test_plain_link_nodes_interleaved_with_other_types(self):
        nodes = [
            TextNode("first [a](u1) node", TextType.PLAIN),
            TextNode("already bold", TextType.BOLD),
            TextNode("second [b](u2) node", TextType.PLAIN),
        ]
        result = split_nodes_link(nodes)
        self.assertEqual(
            texts(result),
            ["first ", "a", " node", "already bold", "second ", "b", " node"],
        )
        self.assertEqual(
            types(result),
            [
                TextType.PLAIN,
                TextType.LINK,
                TextType.PLAIN,
                TextType.BOLD,
                TextType.PLAIN,
                TextType.LINK,
                TextType.PLAIN,
            ],
        )

    def test_output_order_matches_input_order(self):
        nodes = [
            TextNode("[first](u1)", TextType.PLAIN),
            TextNode("[second](u2)", TextType.PLAIN),
        ]
        result = split_nodes_link(nodes)
        self.assertEqual(texts(result), ["first", "second"])

    def test_image_only_text_left_untouched_by_link_fn(self):
        node = TextNode("a ![image](url) only", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "a ![image](url) only")
        self.assertEqual(result[0].text_type, TextType.PLAIN)


if __name__ == "__main__":
    unittest.main()
