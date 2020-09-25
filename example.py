from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import minexr

ETC_PATH = Path(__file__).parent / 'etc'

def main():
    with open(ETC_PATH / 'cube0001.exr', 'rb') as fp:
        reader = minexr.load(fp)
        rgba = reader.select(['Color.R','Color.G','Color.B','Color.A']).astype(np.float32)
        depth = reader.select(['Depth.V']).astype(np.float32)
        normal = reader.select(['Normal.X','Normal.Y','Normal.Z']).astype(np.float32)
        
        plot_maps(rgba, depth, normal)

def plot_maps(rgba, depth, normal):
    normal = (normal * 0.5) + 0.5
    csfont = {'fontname':'Times New Roman'}
    fig, axs = plt.subplots(1,3, figsize=(9,3))
    axs[0].imshow(rgba)
    axs[0].set_title('Linear Color', **csfont)
    axs[0].set_axis_off()
    axs[1].imshow(depth[...,0], cmap='gray_r', vmin=8, vmax=15)
    axs[1].set_title('Linear Depth', **csfont)
    axs[1].set_axis_off()
    axs[2].imshow(normal)
    axs[2].set_title('Normals', **csfont)
    axs[2].set_axis_off()
    plt.tight_layout()
    plt.show()
        


if __name__ == '__main__':
    main()