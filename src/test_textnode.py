import unittest
from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.bold)
        node2 = TextNode("This is a text node", TextType.bold)
        self.assertEqual(node, node2)

    def test_ineq(self):
        node = TextNode("This is a text node", TextType.bold)
        node2 = TextNode("This is a text node", TextType.italic)
        self.assertNotEqual(node, node2)

class TestLinkNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("Google", TextType.link, "https://google.com")
        node2 = TextNode("Google", TextType.link, "https://google.com")
        self.assertEqual(node, node2)

    def test_ineq(self):
        node = TextNode("Google", TextType.link, "https://google.com")
        node2 = TextNode("Google", TextType.link, "https://apple.com")
        self.assertNotEqual(node, node2)

class TestImageNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("image1", TextType.image, "/assets/images/1.jpg")
        node2 = TextNode("image1", TextType.image, "/assets/images/1.jpg")
        self.assertEqual(node, node2)

    def test_ineq(self):
        node = TextNode("image1", TextType.image, "/assets/images/1.jpg")
        node2 = TextNode("image1", TextType.image, "/assets/images/2.jpg")
        self.assertNotEqual(node, node2)

if __name__ == "__main__":
    unittest.main()
