#!/usr/bin/env python3
import os
import sys
import hashlib

GIT_DIR = ".mygit"

def main():
    if len(sys.argv) < 2:
        print("Usage: mygit.py <command> [args]")
        return

    command = sys.argv[1]

    if command == "init":
        init()
    elif command == "hash-object":
        if len(sys.argv) < 3:
            print("Usage: mygit.py hash-object <filename>")
            return
        hash_object(sys.argv[2])
    elif command == "cat-file":
        if len(sys.argv) < 3:
            print("Usage: mygit.py cat-file <hash>")
            return
        cat_file(sys.argv[2])
    else:
        print(f"Unknown command: {command}")

def init():
    os.makedirs(f"{GIT_DIR}/objects", exist_ok=True)
    print("Initialized empty MyGit repository in .mygit/")

def hash_object(filename):
    with open(filename, "rb") as f:
        data = f.read()

    header = f"blob {len(data)}\0".encode()
    store = header + data
    oid = hashlib.sha1(store).hexdigest()
    path = f"{GIT_DIR}/objects/{oid}"

    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(store)

    print(oid)

def cat_file(oid):
    path = f"{GIT_DIR}/objects/{oid}"
    if not os.path.exists(path):
        print(f"Object {oid} not found.")
        return

    with open(path, "rb") as f:
        obj = f.read()

    content = obj.split(b'\x00', 1)[1]
    sys.stdout.buffer.write(content)

if __name__ == "__main__":
    main()
