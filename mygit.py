#!/usr/bin/env python3
import os
import sys
import hashlib
from pathlib import Path

GIT_DIR = ".mygit"
INDEX_FILE = f"{GIT_DIR}/index"

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
    elif command == "checkout":
        if len(sys.argv) < 3:
            print("usage: mygit.py checkout <commit_hash")
            return
        checkout(sys.argv[2])
    elif command == "commit":
        if len(sys.argv) < 3:
            print("Usage: mygit.py commit <message>")
            return
        message = sys.argv[2]
        do_commit(message)
    elif command == "log":
        log()
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: mygit.py add <filename>")
            return
        add(sys.argv[2])
    elif command == "status":
        status()
    elif command == "branch":
        if len(sys.argv) < 3:
            print("Usage: mygit.py branch <branch-name>")
            return
        create_branch(sys.argv[2])
    else:
        print(f"Unknown command: {command}")

def init():
    os.makedirs(f"{GIT_DIR}/objects", exist_ok=True)
    os.makedirs(f"{GIT_DIR}/refs/heads",exist_ok=True)
    with open(f"{GIT_DIR}/HEAD", "w") as f:
        f.write("ref: refs/heads/main")
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

def write_tree_object(entries):
    data = "\n".join(entries).encode()
    header = f"tree {len(data)}\0".encode()
    full_tree = header + data
    oid = hashlib.sha1(full_tree).hexdigest()
    path = f"{GIT_DIR}/objects/{oid}"
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(full_tree)
    return oid

def write_tree():
    if not os.path.exists(INDEX_FILE):
        print("Nothing to write. Index is empty.")
        return None

    entries = []
    with open(INDEX_FILE, "r") as index:
        for line in index:
            oid, filename = line.strip().split(" ", 1)
            entries.append(f"100644 blob {oid} {filename}")

    tree_oid = write_tree_object(entries)
    print(tree_oid)
    return tree_oid

def do_commit(message):

    index_path = f"{GIT_DIR}/index"
    if not os.path.exists(index_path):
        print("Nothing to write. Index is empty.")
        return

    entries = []
    with open(index_path) as f:
        for line in f:
            oid, path = line.strip().split(" ", 1)
            entries.append(f"100644 blob {oid} {path}")

    tree_data = "\n".join(entries).encode()
    tree_header = f"tree {len(tree_data)}\0".encode()
    tree_object = tree_header + tree_data
    tree_oid = hashlib.sha1(tree_object).hexdigest()

    with open(f"{GIT_DIR}/objects/{tree_oid}", "wb") as f:
        f.write(tree_object)

    head_path = f"{GIT_DIR}/HEAD"
    parent = ""

    if os.path.exists(head_path):
        with open(head_path, "r") as f:
            head_content = f.read().strip()
            if head_content.startswith("ref: "):
                ref_path = f"{GIT_DIR}/{head_content[5:]}"
                if os.path.exists(ref_path):
                    with open(ref_path, "r") as rf:
                        parent = rf.read().strip()
            else:
                parent = head_content  # detached HEAD

    commit_content = f"tree {tree_oid}\n"
    if parent:
        commit_content += f"parent {parent}\n"
    commit_content += f"\n{message}\n"

    commit_header = f"commit {len(commit_content)}\0".encode()
    commit_data = commit_header + commit_content.encode()
    commit_oid = hashlib.sha1(commit_data).hexdigest()

    with open(f"{GIT_DIR}/objects/{commit_oid}", "wb") as f:
        f.write(commit_data)

    if head_content.startswith("ref: "):
        ref_path = f"{GIT_DIR}/{head_content[5:]}"
        os.makedirs(os.path.dirname(ref_path), exist_ok=True)
        with open(ref_path, "w") as f:
            f.write(commit_oid)
    else:
        with open(head_path, "w") as f:
            f.write(commit_oid)  # detached HEAD update

    os.remove(index_path)

    print(commit_oid)

def log():
    head_path = f"{GIT_DIR}/HEAD"
    if not os.path.exists(head_path):
        print("No commits yet.")
        return

    with open(head_path, "r") as f:
        oid = f.read().strip()

    while oid:
        path = f"{GIT_DIR}/objects/{oid}"
        with open(path, "rb") as f:
            obj = f.read()

        content = obj.split(b"\x00", 1)[1].decode()

        print(f"commit {oid}")
        print(content)
        print("-" * 30)

        # find next parent
        lines = content.splitlines()
        parent = None
        for line in lines:
            if line.startswith("parent "):
                parent = line.split(" ", 1)[1]
                break

        if parent:
            oid = parent
        else:
            break

def add(filename):
    oid = hash_object(filename)

    # Update index
    index_path = f"{GIT_DIR}/index"
    with open(index_path, "a") as idx:
        idx.write(f"{oid} {filename}\n")

def status():
    index_path = f"{GIT_DIR}/index"
    head_path = f"{GIT_DIR}/HEAD"

    index = {}
    if os.path.exists(index_path):
        with open(index_path) as f:
            for line in f:
                oid, path = line.strip().split(" ", 1)
                index[path] = oid

    head_tree = {}
    if os.path.exists(head_path):
        with open(head_path) as f:
            head_commit_oid = f.read().strip()
        commit_path = f"{GIT_DIR}/objects/{head_commit_oid}"
        if os.path.exists(commit_path):
            with open(commit_path, "rb") as f:
                commit = f.read().split(b"\x00", 1)[1].decode()
            for line in commit.splitlines():
                if line.startswith("tree "):
                    tree_oid = line[5:].strip()
                    tree_path = f"{GIT_DIR}/objects/{tree_oid}"
                    with open(tree_path, "rb") as f:
                        tree = f.read().split(b"\x00", 1)[1].decode()
                    for entry in tree.splitlines():
                        parts = entry.split(" ")
                        if len(parts) == 4:
                            _, _, oid, path = parts
                            head_tree[path] = oid

    all_files = set()
    for path in Path(".").rglob("*"):
        if path.is_file() and GIT_DIR not in path.parts:
            all_files.add(str(path))

    staged = []
    unstaged = []
    untracked = []

    for path in sorted(all_files):
        with open(path, "rb") as f:
            data = f.read()
        header = f"blob {len(data)}\0".encode()
        oid = hashlib.sha1(header + data).hexdigest()

        if path in index:
            if index[path] != oid:
                unstaged.append(path)
            else:
                staged.append(path)
        else:
            untracked.append(path)

    print("Staged for commit:")
    for path in staged:
        print(f"  {path}")
    print("\nModified but not staged:")
    for path in unstaged:
        print(f"  {path}")
    print("\nUntracked files:")
    for path in untracked:
        print(f"  {path}")

def checkout(commit_hash):
    ref_path = os.path.join(GIT_DIR, "refs", "heads", commit_hash)
    if os.path.exists(ref_path):
        with open(ref_path, "r") as f:
            commit_hash = f.read().strip()
        # update HEAD to track this branch
        with open(os.path.join(GIT_DIR, "HEAD"), "w") as f:
            f.write(f"ref: refs/heads/{commit_hash}")
    commit_path = f"{GIT_DIR}/objects/{commit_hash}"
    if not os.path.exists(commit_path):

        print(f"Commit {commit_hash} not found.")
        return

    with open(commit_path, "rb") as f:
        commit_data = f.read()

    split = commit_data.split(b'\x00', 1)
    if len(split) != 2:
        print("Invalid commit format")
        return
    content = split[1].decode()

    # Get tree hash
    tree_line = content.splitlines()[0]
    if not tree_line.startswith("tree "):
        print("Not a valid commit")
        return
    tree_hash = tree_line[5:]

    # Read the tree object
    tree_path = os.path.join(GIT_DIR, "objects", tree_hash)
    if not os.path.exists(tree_path):
        print(f"Tree object {tree_hash} not found.")
        return

    with open(tree_path, "rb") as f:
        tree_data = f.read()

    tree_content = tree_data.split(b'\x00', 1)[1].decode()

    tracked_files = []
    for line in tree_content.splitlines():
        _, _, oid, filename = line.split(" ", 3)
        tracked_files.append((filename, oid))

    # Only remove files that differ from the new commit's version
    for filename, oid in tracked_files:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                existing = f.read()
            header = f"blob {len(existing)}\0".encode()
            current_oid = hashlib.sha1(header + existing).hexdigest()
            if current_oid != oid:
                os.remove(filename)

    # Write checked out files
    for filename, oid in tracked_files:
        obj_path = os.path.join(GIT_DIR, "objects", oid)
        with open(obj_path, "rb") as f:
            obj_data = f.read()
        file_data = obj_data.split(b'\x00', 1)[1]
        with open(filename, "wb") as f:
            f.write(file_data)

    with open(os.path.join(GIT_DIR, "HEAD"), "w") as f:
        f.write(commit_hash)

    print(f"Checked out commit {commit_hash}")

def create_branch(name):
    head_path = f"{GIT_DIR}/HEAD"
    with open(head_path, "r") as f:
        ref = f.read().strip()

    if ref.startswith("ref: "):
        ref_path = f"{GIT_DIR}/{ref[5:]}"
        if os.path.exists(ref_path):
            with open(ref_path, "r") as f:
                oid = f.read().strip()
        else:
            print("No commits yet.")
            return
    else:
        oid = ref

    branch_path = f"{GIT_DIR}/refs/heads/{name}"
    with open(branch_path, "w") as f:
        f.write(oid)

    print(f"Created branch {name} at {oid}")

if __name__ == "__main__":
    main()
