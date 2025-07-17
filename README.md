# MyGit

MyGit is a minimal, from-scratch Git clone built in Python. It implements essential version control functionality using a simple `.mygit` directory and mimics Git’s object model and CLI.

## Features

- `mygit.py init` — Initialize a new repository
- `mygit.py add <filename>` — Add files to the staging index
- `mygit.py commit <message>` — Save a snapshot of staged files
- `mygit.py log` — View the commit history
- `mygit.py status` — See staged, modified, and untracked files
- `mygit.py hash-object <filename>` — Store raw file as a Git object
- `mygit.py cat-file <hash>` — Read the contents of an object
- `mygit.py write-tree` — Write current staging index to a tree
- `mygit.py checkout <commit-hash>` — Restore working directory to a previous commit
- `mygit.py branch <name>` — Create a new branch from current commit
-` mygit.py status` — Show modified, staged, and untracked files (now works like real Git!)
- `mygit.py branch <name>` — Create a new branch
- `mygit.py checkout <commit-hash|branch>` — Switch to a commit or branch


## Example Workflow

```bash
./mygit.py init
echo "Hello" > file.txt
./mygit.py add file.txt
./mygit.py commit "Initial commit"
./mygit.py log

