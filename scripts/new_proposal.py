from argparse import ArgumentParser
import os
import shutil

from tools import title_to_slug, FepFile


def build_parser():
    parser = ArgumentParser("Create new FEP proposal")
    parser.add_argument("title", nargs="+")

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    title = " ".join(args.title)
    slug = title_to_slug(title)

    try:
        os.mkdir(f"fep/{slug}")
    except Exception as e:
        print("During directory creation ", repr(e))

    filename = f"fep/{slug}/fep-{slug}.md"

    if os.path.exists(filename):
        print("FEP already exists")
        exit(1)
    else:
        shutil.copyfile("fep-xxxx-template.md", filename)

    fep = FepFile(slug)

    fep.frontmatter = [f'slug: "{slug}"'] + fep.frontmatter[1:]
    fep.content = [f"# FEP-{slug}: {title}"] + fep.content[1:]

    fep.write()

    print(f"New FEP proposal created at {filename}")
