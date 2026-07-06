import sys

from generate_content import generate_site
from static_copy import static_copy


def main():
    argv = sys.argv[1:]
    if len(argv) > 1:
        raise Exception("Don't know what you're doing")
    basepath = argv[0]
    if basepath == "":
        basepath = "/"
    static_copy()
    generate_site(src_path="./content", dest_path="./docs", base_path=basepath)


if __name__ == "__main__":
    main()
