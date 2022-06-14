from pathlib import Path

import numpy as np
from PIL import Image

from ..reader import MinExrReader

ETC_PATH = Path(__file__).parent / '..' / '..' / 'etc'

def test_parse_files():
    with open(ETC_PATH/'cube0001.exr', 'rb') as fp:
        minr = MinExrReader(fp)
        rgba = minr.select(['Color.R','Color.G','Color.B','Color.A']).astype(np.float32)
        depth = minr.select(['Depth.V']).astype(np.float32)
        normal = minr.select(['Normal.X','Normal.Y','Normal.Z']).astype(np.float32)
        normal = (normal * 0.5) + 0.5

        t_rgba = np.asarray(Image.open(ETC_PATH/'Color0001.png').convert('RGBA')) / 255.0
        t_normal = np.asarray(Image.open(ETC_PATH/'Normal0001.png').convert('RGB')) / 255.0

        np.testing.assert_allclose(rgba, t_rgba, atol=1e-2)
        np.testing.assert_allclose(normal, t_normal, atol=1e-2)
    
    with open(ETC_PATH/'cube0002.exr', 'rb') as fp:
        minr = MinExrReader(fp)
        rgba = minr.select(['View Layer.Combined.R','View Layer.Combined.G','View Layer.Combined.B','View Layer.Combined.A']).astype(np.float32)
        depth = minr.select(['View Layer.Depth.Z']).astype(np.float32)
        normal = minr.select(['View Layer.Normal.X','View Layer.Normal.Y','View Layer.Normal.Z']).astype(np.float32)
        normal = (normal * 0.5) + 0.5
        
        t_rgba = np.asarray(Image.open(ETC_PATH/'Color0002.png').convert('RGBA')) / 255.0
        t_normal = np.asarray(Image.open(ETC_PATH/'Normal0002.png').convert('RGB')) / 255.0

        np.testing.assert_allclose(rgba, t_rgba, atol=1e-2)
        np.testing.assert_allclose(normal, t_normal, atol=1e-2)

def test_select():
    with open(ETC_PATH/'cube0001.exr', 'rb') as fp:
        minr = MinExrReader(fp)
        H,C,W = minr.shape
        assert H == 270
        assert W == 480
        assert C == 3 + 4 + 1

        img = minr.select(['Color.R', 'Color.G', 'Color.B'])
        assert img.base is minr.image
        assert img.shape == (H,W,3)
        img = minr.select(['Color.B', 'Color.G', 'Color.R']) # negative stepping
        assert img.base is minr.image
        assert img.shape == (H,W,3)
        img = minr.select(['Color.R', 'Color.B'])
        assert img.base is minr.image
        assert img.shape == (H,W,2)
        img = minr.select(minr.channel_names)
        assert img.base is minr.image
        assert img.shape == (H,W,C)
        img = minr.select(minr.channel_names[::-1], channels_last=False)
        assert img.base is minr.image
        assert img.shape == (H,C,W)

        img = minr.select([])
        assert img.size == 0
        img = minr.select(['Color.R', 'Depth.V', 'Color.B'])
        assert img.base is not minr.image
        assert img.shape == (H,W,3)
        
    with open(ETC_PATH/'cube0002.exr', 'rb') as fp:
        minr = MinExrReader(fp)
        H,C,W = minr.shape
        assert H == 270
        assert W == 480
        assert C == 3 + 4 + 1

        img = minr.select(['View Layer.Combined.R', 'View Layer.Combined.G', 'View Layer.Combined.B'])
        assert img.base is minr.image
        assert img.shape == (H,W,3)
        img = minr.select(['View Layer.Combined.B', 'View Layer.Combined.G', 'View Layer.Combined.R']) # negative stepping
        assert img.base is minr.image
        assert img.shape == (H,W,3)
        img = minr.select(['View Layer.Combined.R', 'View Layer.Combined.B'])
        assert img.base is minr.image
        assert img.shape == (H,W,2)
        img = minr.select(minr.channel_names)
        assert img.base is minr.image
        assert img.shape == (H,W,C)
        img = minr.select(minr.channel_names[::-1], channels_last=False)
        assert img.base is minr.image
        assert img.shape == (H,C,W)

        img = minr.select([])
        assert img.size == 0
        img = minr.select(['View Layer.Combined.R', 'View Layer.Depth.Z', 'View Layer.Combined.B'])
        assert img.base is not minr.image
        assert img.shape == (H,W,3)



    # plt.figure()
    # img = r.select(['Color.R', 'Color.G', 'Color.B'])
    # print(img.base is r.image)
    # img = r.select(['Depth.V'])
    # print(img.base is r.image)
    # img = r.select(['Color.R', 'Depth.V'])
    # print(img.base is r.image)
    # img = r.select(['Color.R', 'Depth.V', 'Color.B'])
    # print(img.base is r.image)
        
    #     fig, axs = plt.subplots(1,3, figsize=(16,3))
    #     axs[0].imshow(rgba)
    #     axs[0].set_title('Linear Color')
    #     axs[0].set_axis_off()
    #     axs[1].imshow(depth[...,0], cmap='gray_r', vmin=8, vmax=15)
    #     axs[1].set_title('Linear Depth')
    #     axs[1].set_axis_off()
    #     axs[2].imshow(normal)
    #     axs[2].set_title('Normals')
    #     axs[2].set_axis_off()
    #     plt.tight_layout()
    #     plt.show()
