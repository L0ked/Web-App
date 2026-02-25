import sys
import os

if __name__ == '__main__':
    directory = sys.argv[1]

    files = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isfile(full_path):
            files.append(item)

    files_by_ext = {}
    for file in files:
        if '.' in file:
            ext = file.split('.')[-1]
        else:
            ext = ''
        if ext not in files_by_ext:
            files_by_ext[ext] = []
        files_by_ext[ext].append(file)

    for ext in sorted(files_by_ext.keys()):
        for file in sorted(files_by_ext[ext]):
            print(file)
