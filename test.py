import os

current_dir = os.getcwd()
base_dir = os.path.join(current_dir, 'tmp')
os.makedirs(base_dir, exist_ok=True)
src_path = os.path.join(base_dir, 'temp.ts')

with open(src_path, "w") as file:
    file.write("hola")