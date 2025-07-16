# MyGit

A simple implementation of Git features in Python, built from scratch to understand how version control works under the hood.

## Features Implemented

- Repository initialization (`init`)
- Object storage using SHA-1 hashes (`hash-object`)
- Object inspection (`cat-file`)

## Upcoming Features

- Tree and commit creation (`write-tree`, `commit`)
- Simple version tracking
- Commit history/log

## How to Run

```bash
# Initialize your repo
python mygit.py init

# Hash a file
python mygit.py hash-object <filename>

# Print a stored object
python mygit.py cat-file <hash>
