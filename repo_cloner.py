from git import Repo

def git_clone(clone_from, clone_to):
    Repo.clone_from(clone_from, clone_to)
