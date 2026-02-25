#!/usr/bin/env python3
"""Build script: freezes all Flask labs into a single static site."""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(ROOT, 'site')

def build_lab(lab_name):
    lab_dir = os.path.join(ROOT, lab_name)
    if not os.path.isdir(lab_dir):
        return False
    freeze_script = os.path.join(lab_dir, 'freeze.py')
    if not os.path.isfile(freeze_script):
        return False

    print(f'=== Building {lab_name} ===')

    req_file = os.path.join(lab_dir, 'requirements.txt')
    if os.path.isfile(req_file):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file, '-q', '--break-system-packages'])

    subprocess.check_call([sys.executable, freeze_script], cwd=lab_dir)

    build_dir = os.path.join(lab_dir, 'build')
    dest = os.path.join(SITE_DIR, lab_name)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(build_dir, dest)
    print(f'{lab_name} → site/{lab_name}')
    return True

def main():
    if os.path.exists(SITE_DIR):
        shutil.rmtree(SITE_DIR)
    os.makedirs(SITE_DIR)

    # Copy root index.html
    shutil.copy2(os.path.join(ROOT, 'index.html'), os.path.join(SITE_DIR, 'index.html'))

    # Find and build all labs
    labs = sorted(d for d in os.listdir(ROOT) if d.startswith('lab') and os.path.isdir(os.path.join(ROOT, d)))
    for lab in labs:
        build_lab(lab)

    print(f'\n✅ Site built in site/')

if __name__ == '__main__':
    main()
