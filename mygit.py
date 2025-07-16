#!/usr/bin/env python3
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: mygit.py <command>")
        return

    command = sys.argv[1]

    if command == "init":
        init()
    else:
        print(f"Unknown command: {command}")

def init():
    os.makedirs(".mygit/objects", exist_ok=True)
    print("Initialized empty MyGit repository in .mygit/")

if __name__ == "__main__":
    main()
