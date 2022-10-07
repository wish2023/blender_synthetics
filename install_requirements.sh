#!/bin/bash

# Ensure pip: equl to /blender-path/3.xx/python/bin/python3.10 -m ensurepip
blender -b --python-expr "from subprocess import sys,call;call([sys.executable,'-m','ensurepip'])"
# Update pip toolchain
blender -b --python-expr "from subprocess import sys,call;call([sys.executable]+'-m pip install -U pip setuptools wheel'.split())"
# pip install
blender -b --python-expr "from subprocess import sys,call;call([sys.executable]+'-m pip install -U bpycv'.split());call([sys.executable]+'-m pip install -U PyYAML'.split());call([sys.executable]+'-m pip install -U glob2'.split())"

pip install -r requirements.txt