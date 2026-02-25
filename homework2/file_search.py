import sys
import os

if __name__ == '__main__':
    filename = sys.argv[1]
    found = False

    for root, dirs, files in os.walk('.'):
        if filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:5]):
                        print(line, end='')
                    found = True
                    break
            except:
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines[:5]):
                            print(line, end='')
                        found = True
                        break
                except:
                    pass

    if not found:
        print(f"Файл {filename} не найден")
