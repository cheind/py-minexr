from pathlib import Path
import numpy as np
import timeit, functools

# Only benchmark requires OpenEXR installed
import OpenEXR, Imath
import minexr

FNAME = str(Path(__file__).parent / 'etc' / 'cube0001.exr')
N = 100

def read_openexr(fname):
    file = OpenEXR.InputFile(fname)    
    header = file.header()
    dw = header['dataWindow']
    pt = Imath.PixelType(Imath.PixelType.HALF)
    shape = (dw.max.y - dw.min.y + 1, dw.max.x - dw.min.x + 1)
    r = np.frombuffer(file.channel('Color.R', pt), dtype=np.float16).reshape(shape + (1,))
    g = np.frombuffer(file.channel('Color.G', pt), dtype=np.float16).reshape(shape + (1,))
    b = np.frombuffer(file.channel('Color.B', pt), dtype=np.float16).reshape(shape + (1,))
    a = np.frombuffer(file.channel('Color.A', pt), dtype=np.float16).reshape(shape + (1,))
    img = np.concatenate((r,g,b,a),-1).astype(np.float32)
    file.close()
    return img

def read_minexr(fname):
    with open(fname, 'rb') as fp:
        reader = minexr.load(fp)
        rgba = reader.select(['Color.R','Color.G','Color.B','Color.A']).astype(np.float32)
        return rgba

def main():
    
    t = timeit.Timer(functools.partial(read_openexr, FNAME))
    print(f'Average read time OpenEXR: {(t.timeit(100)/100):.3f} sec/image')

    t = timeit.Timer(functools.partial(read_minexr, FNAME))
    print(f'Average read time minexr: {(t.timeit(100)/100):.3f} sec/image')
        


if __name__ == '__main__':
    main()