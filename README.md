# minexr

**minexr** is a standalone, fast Python [OpenEXR](https://www.openexr.com/) reader for single-part, uncompressed scan-line files. It is compatible with `.exr` files produced by [Blender](http://blender.org).

## Assumptions
**minexr** makes a couple of assumptions about the `.exr` file to be read:
 1. single-part files with arbitrary number of channels,
 1. no pixel data compression, and
 1. equal channel types (HALF, FLOAT, UINT).

These assumptions allow us to efficiently parse and read the `.exr` file. In particular we gain constant offsets between scan lines which allows us to read the entire image in (H,C,W) format without copying.

## Usage
The following is taken from [example.py](./example.py)
```python
import minexr

with open('file.exr', 'rb') as fp:
        reader = minexr.load(fp)
        rgba = reader.select(['Color.R','Color.G','Color.B'])
        # a HxWx3 np.array with dtype based on exr type.
        ...
```
Full [example.py](./example.py) loads the following images
<p align="center">
  <img  src="etc/result.png">
</p>

which were previously rendered using Blender/EEVEE [cube.blend](./etc/cube.blend).

## Runtime
The following timings are produced by [bench.py](./bench.py) by repeatable reading an RGBA image from an `.exr` file. Timings include file and numpy operations.

|Module|[sec/image]|Note|
|:----:|:---------:|-------|
|OpenEXR 1.3.2|0.020|with channel concatenate|
|OpenEXR 1.3.2|0.015|without channel concatenate|
|**minexr**|**0.004**|with channel concatenate|

## Install
Clone and invoke
```
pip install -e .
``` 

## Tests
