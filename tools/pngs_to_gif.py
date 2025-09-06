from PIL import Image
from pathlib import Path

def main():
    frames = sorted(Path('captures').glob('menu_*.png'))
    if not frames:
        print('No frames found in captures/')
        return
    imgs = [Image.open(p).convert('P', palette=Image.ADAPTIVE) for p in frames]
    imgs[0].save('menu_dragons.gif', save_all=True, append_images=imgs[1:], loop=0, duration=33, optimize=True)
    print('Saved menu_dragons.gif')

if __name__ == '__main__':
    main()
