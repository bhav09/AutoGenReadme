import seedir as sd
import sys

def tree(clone_to):
    stdout = sys.stdout
    f = open(f'{clone_to}/tree.txt', 'w')
    sys.stdout = f

    sd.seedir(clone_to, style='emoji', depthlimit=2, exclude_folders=['.git', '.gitkeep'])
    sys.stdout = stdout
    # f.close()
