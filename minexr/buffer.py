import ctypes

class BufferReader:
    '''A lightweight io.BytesIO object with convenience functions.
    
    Params
    ------
    data : bytes-like
        Bytes for which random access is required.
    
    '''

    def __init__(self, data):
        self.data = data
        self.len = len(data)
        self.off = 0

    def read(self, n):
        '''Read next `n` bytes.'''
        v = self.data[self.off:self.off+n]
        self.off += n
        return v

    def read_null_string(self):
        '''Read a null-terminated string.'''
        s = ctypes.create_string_buffer(self.data[self.off:]).value
        if s != None:
            s = s.decode('utf-8')
            self.off += len(s) + 1
        return s

    def peek(self):
        '''Peek next byte.'''
        return self.data[self.off]

    def advance(self, n):
        '''Advance offset by `n` bytes.'''
        self.off += n

    def nleft(self):
        '''Returns the number of bytes left to read.'''
        return self.len - self.off - 1