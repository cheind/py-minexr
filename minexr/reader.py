import numpy as np
import struct

from .buffer import BufferReader

class MinExrReader:
    '''Minimal, standalone OpenEXR reader for single-part, uncompressed scan line files.

    This OpenEXR reader makes a couple of assumptions
     - single-part files with arbitrary number of channels,
     - no pixel data compression, and
     - equal channel types (HALF, FLOAT, UINT).

    These assumptions allow us to efficiently parse and read the `.exr` file. In particular
    we gain constant offsets between scan lines which allows us to read the entire image
    in (H,C,W) format without copying.

    Use `MinimalEXR.select` to select a subset of channels in the given order. `MinimalEXR.select`
    tries to be smart when copying is required and when views are ok.
    
    Based on the file format presented in
    https://www.openexr.com/documentation/openexrfilelayout.pdf

    Attributes
    ----------
    shape: tuple
        Shape of image in (H,C,W) order
    image: numpy.array
        Uncompressed image data.
    attrs: dict
        OpenEXR header attributes.
    '''

    def __init__(self, fp):
        self.fp = fp
        self.image = None
        self.shape = None

        self._read_header()
        self._read_image()

    def select(self, channels, channels_last=True):
        '''Returns an image composed only of the given channels.
        
        Attempts to be smart about memory views vs. memory copies.

        Params
        ------
        channels: list-like
            Names of channels to be extracted. Appearance in list
            also defines the order of the channels. 
        channels_last: bool, optional
            When true return image in (H,W,C) format.

        Returns
        -------
        image: HxWxC or HxCxW array
            Selected image data.
        '''
        H,C,W = self.shape
        ids = [self.channel_map[c] for c in channels]                
        if len(ids) == 0:
            img = np.empty((H,0,W), dtype=self.image.dtype)
        else:
            diff = np.diff(ids)
            sH = slice(0, H)
            sW = slice(0, W)
            if len(diff) == 0:
                # single channel select, return view
                sC = slice(ids[0],ids[0]+1)
                img = self.image[sH,sC,sW]
            elif len(set(diff)) == 1:
                # mutliple channels, constant offset between, return view
                # Careful here with negative steps, ie. diff[0] < 0:
                start = ids[0]
                step = diff[0]
                end = ids[-1]+diff[0]
                end = None if end < 0 else end                
                sC = slice(start,end,step)
                img = self.image[sH,sC,sW]
            else:
                # multiple channels not slicable -> copy mem
                chdata = [self.image[sH,i:i+1,sW] for i in ids]
                img = np.concatenate(chdata, 1)
        
        if channels_last:
            img = img.transpose(0,2,1)
        return img

    def _read_header(self):
        self.fp.seek(0)        
        buf = BufferReader(self.fp.read(10000))

        # Magic and version and info bits
        magic, version, b2, b3, b4 = struct.unpack('<iB3B', buf.read(8))
        assert magic == 20000630, 'Not an OpenEXR file.'
        assert b2 in (0, 4), 'Not a single-part scan line file.'
        assert b3 == b4 == 0, 'Unused flags in version field are not zero.'

        # Header attributes
        self.attrs = self._read_header_attrs(buf)

        # Parse channels and datawindow
        self.compr = self._parse_compression(self.attrs)        
        self.channel_names, self.channel_types = self._parse_channels(self.attrs)
        self.channel_map = {cn:i for i,cn in enumerate(self.channel_names)}
        H, W = self._parse_data_window(self.attrs)
        self.shape = (H,len(self.channel_names),W)
        self.first_offset = self._read_first_offset(buf)
        
        # Assert our assumptions
        assert self.compr == 0x00, 'Compression not supported.'
        assert len(set(self.channel_types)) <= 1, 'All channel types must be equal.'

    def _read_image(self):
        # Here is a shortcut: We assume all channels of the same type and thus constant offsets between
        # scanlines (SOFF). Note, each scanline has a header (y-coordinate (int4), data size DS (int4)) and data in scanlines
        # is stored consecutively for channels (in order of appearance in header). Thus we can interpret the content
        # as HxCxW image with strides: (SOFF,DS*W,DS)
        H,C,W = self.shape

        if np.prod(self.shape) == 0:
            return np.empty(self.shape, dtype=np.float32)

        dtype  = self.channel_types[0]
        DS = np.dtype(dtype).itemsize
        SOFF = 8+DS*W*C        
        strides = (SOFF, DS*W, DS)
        nbytes = SOFF*H

        self.fp.seek(self.first_offset, 0)
        image = np.frombuffer(self.fp.read(nbytes), dtype=dtype, count=-1, offset=8)
        self.image = np.lib.stride_tricks.as_strided(image, (H,C,W), strides)

    def _read_header_attrs(self, buf):
        attrs = {}
        while buf.nleft() > 0:
            attr = self._read_header_attr(buf)
            if attr is None:
                break
            attrs[attr[0]] = attr
        return attrs

    def _read_header_attr(self, buf):
        if buf.peek() == 0x00:
            buf.advance(1)
            return None
        aname = buf.read_null_string()
        atype = buf.read_null_string()
        asize = struct.unpack('<i', buf.read(4))[0]
        data = buf.read(asize)
        return (aname, atype, asize, data)

    def _parse_channels(self, attrs):
        attr = attrs['channels']
        assert attr[1] == 'chlist', 'Unexcepted type for channels attribute.'
        buf = BufferReader(attr[-1])
        channel_names, channel_types = [], []
        PT_LOOKUP = [np.uint32, np.float16, np.float32]
        while buf.nleft() > 0 and buf.peek() != 0x00:            
            channel_names.append(buf.read_null_string())
            pt = struct.unpack('<i', buf.read(4))[0]
            channel_types.append(PT_LOOKUP[pt])
            buf.advance(12) # skip remaining entries
        if buf.nleft() > 0:
            buf.advance(1) # account for zero byte
        return channel_names, channel_types

    def _parse_data_window(self, attrs):
        attr = attrs['dataWindow']
        assert attr[1] == 'box2i', 'Unexcepted type for dataWindow attribute.'
        xmin, ymin, xmax, ymax = struct.unpack('<iiii', attr[-1])
        return (ymax-ymin+1, xmax-xmin+1)

    def _parse_compression(self, attrs):
        return attrs['compression'][-1][0]

    def _read_offsets(self, buf):
        offsets = []
        while buf.nleft() > 0 and buf.peek() != 0x00:
            o = struct.unpack('<Q', buf.read(8))[0]
            offsets.append(o)
        if buf.nleft() > 0:
            buf.advance(1) # account for zero byte
        return offsets

    def _read_first_offset(self, buf):
        assert buf.nleft() > 0 and buf.peek() != 0x00, 'Failed to read offset.'
        return struct.unpack('<Q', buf.read(8))[0]


def load(fp):
    return MinExrReader(fp)
