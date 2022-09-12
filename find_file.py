import os
import glob

texture_path = "/home/vishesh/Downloads/terrain"

search = os.path.join(texture_path, "*_diff_*")

print(glob.glob(search))