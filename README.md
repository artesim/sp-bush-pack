The bush_packer is written in python 3.8 and doesn't require any external package as of yet.

The bush pack sources are available in /bush_pash_sources

I use the winpython distribution, available as a portable installation here :
https://github.com/winpython/winpython/releases/tag/3.0.20200808

Take the minimal package (dubbed 'dot'), such as this one :
https://github.com/winpython/winpython/releases/download/3.0.20200808/Winpython64-3.8.5.0dot.exe

Once installed, run the packer with :
```sh
$ <path-to-python.exe> <sp-bush-pack-dir>\main.py <example-bush-pack-source-dir> <output-dir>
```

Please note that the `<output-dir>/<bush-pack-name>` directory will be completely overwritten .

Example with provided example bush pack:
```sh
$ E:\winpython\WPy64-3850\python-3.8.5.amd64\python.exe E:\sp-bush-pack\main.py E:\sp-bush-pack\bush_pack_sources\example-bush-pack E:\sp-bush-pack\dist
```
=> Generate (and overwrites) the bush pack in E:\sp-bush-pack\dist\example-bush-pack
