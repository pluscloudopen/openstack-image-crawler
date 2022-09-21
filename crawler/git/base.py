import git
# from pprint import pprint
from pathlib import Path


def clone_or_pull(remote_repository, repository):
    path = Path(repository)
    if not path.is_dir():
        print("Cloning repositoy %s into %s" % (remote_repository, repository))
        try:
            git.Repo.clone_from(remote_repository, repository)
        except git.exc.GitCommandError as error:
            raise SystemExit("FATAL: Cloning of %s failed with %s" % (remote_repository, error))
    else:
        print("Repository exists already, pulling changes")
        image_repo = git.Repo(repository)
        try:
            image_repo.remotes.origin.pull()
        except git.exc.GitCommandError as error:
            raise SystemExit("FATAL: Update (pull) failed with %s" % error)


def update_repository(repository):
    image_repo = git.Repo(repository)
    if image_repo.is_dirty(untracked_files=True):
        print("\nChanges detected.\n")

        all_changes = []

        untracked_files = image_repo.untracked_files
        if untracked_files:
            print("New files:")
            for file in untracked_files:
                print(file)
                all_changes.append(file)

        changed_files = image_repo.git.diff(None, name_only=True)
        if changed_files:
            print("Updated files:")
            for file in changed_files.split('\n'):
                print(file)
                all_changes.append(file)

        image_repo.git.add(all_changes)
        image_repo.index.commit('Updated.')

    try:
        image_repo.remotes.origin.push()
    except Exception as error:
        print("ERROR: Push into upstream repository failed %s " % error)
