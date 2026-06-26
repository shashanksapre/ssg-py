from textnode import TextNode, TextType

def main():
    t_node = TextNode("This is some anchor text", TextType.link, "https://www.boot.dev")

    print(t_node)

if __name__ == "__main__":
    main()