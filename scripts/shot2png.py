# Convert a CS2 screenshot TGA to a downsized PNG for review. Usage: shot2png.py <in.tga> <out.png>
# CS2 under Vulkan writes the swapchain's BGRA bytes as-is, so the TGA's red and blue come out swapped.
import sys
from PIL import Image
r,g,b=Image.open(sys.argv[1]).convert('RGB').split(); im=Image.merge('RGB',(b,g,r)); im.thumbnail((1400,1400)); im.save(sys.argv[2])
