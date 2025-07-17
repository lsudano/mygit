#!/usr/bin/env python3
import os
import sys
import hashlib
from pathlib import Path

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
    elif command == "write-tree":
        write_tree()
    elif command == "commit":
        if len(sys.argv) < 3:
            print("Usage: mygit.py commit <message>")
            return
        message = sys.argv[2]
        do_commit(message)
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
    return oid

def cat_file(oid):
    path = f"{GIT_DIR}/objects/{oid}"
    if not os.path.exists(path):
        print(f"Object {oid} not found.")
        return

    with open(path, "rb") as f:
        obj = f.read()

    content = obj.split(b'\x00', 1)[1]
    sys.stdout.buffer.write(content)

def write_tree():
    entries = []

    for path in sorted(Path(".").rglob("*")):
        if ".mygit" in path.parts or path.is_dir():
            continue

        with open(path, "rb") as f:
            data = f.read()

        header = f"blob {len(data)}\0".encode()
        store = header + data
        oid = hashlib.sha1(store).hexdigest()

        obj_path = f"{GIT_DIR}/objects/{oid}"
        if not os.path.exists(obj_path):
            with open(obj_path, "wb") as out:
                out.write(store)

        entries.append(f"100644 blob {oid} {path.as_posix()}")

    result = "\n".join(entries).encode()
    tree_header = f"tree {len(result)}\0".encode()
    full_tree = tree_header + result

    tree_oid = hashlib.sha1(full_tree).hexdigest()
    tree_path = f"{GIT_DIR}/objects/{tree_oid}"

    if not os.path.exists(tree_path):
        with open(tree_path, "wb") as f:
            f.write(full_tree)

    print(tree_oid)
    return tree_oid

def do_commit(message):
    tree = write_tree()
    content = f"tree {tree}\n\n{message}\n".encode()

    header = f"commit {len(content)}\0".encode()
    full_commit = header + content
    oid = hashlib.sha1(full_commit).hexdigest()

    path = f"{GIT_DIR}/objects/{oid}"
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(full_commit)

    with open(f"{GIT_DIR}/HEAD", "w") as f:
        f.write(oid + "\n")

    print(oid)

if __name__ == "__main__":
    main()
