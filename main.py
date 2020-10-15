from bush_packer.config import CFG
from bush_packer.bush_pack import BushPack
from pathlib import Path


# TODO: formatting the xml => beautiful soup

def main():
    bush_pack = BushPack.load(CFG.src_dir)
    bush_pack.build(CFG.dist_dir)


if __name__ == '__main__':
    main()
