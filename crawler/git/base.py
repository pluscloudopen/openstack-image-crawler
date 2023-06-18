import git
import os
from loguru import logger
from pathlib import Path

from crawler.core.database import db_get_release_versions


def clone_or_pull(remote_repository, repository, working_branch, ssh_command):
    if ssh_command:
        os.environ["GIT_SSH_COMMAND"] = ssh_command
    path = Path(repository)
    if not path.is_dir():
        logger.info(
            "Cloning repository %s (%s) into %s"
            % (remote_repository, working_branch, repository)
        )
        try:
            image_repo = git.Repo.clone_from(
                remote_repository, repository, branch=working_branch
            )
        except git.exc.GitCommandError as error:
            logger.error("Cloning of %s failed with %s" %
                         (remote_repository, error))
            raise SystemExit(1)
    else:
        logger.info("Repository exists already, pulling changes (%s)" %
                    working_branch)
        image_repo = git.Repo(repository)
        try:
            image_repo.remotes.origin.pull()
        except git.exc.GitCommandError as error:
            logger.error("Update (pull) failed with %s" % error)
            raise SystemExit(1)

        try:
            image_repo.git.checkout(working_branch)
        except git.exc.GitCommandError as error:
            logger.error(
                "Checkout on branch %s failed with %s" %
                (working_branch, error)
            )
            raise SystemExit(1)


def update_repository(database, repository, updated_sources, ssh_command):
    if ssh_command:
        os.environ["GIT_SSH_COMMAND"] = ssh_command
    image_repo = git.Repo(repository)
    if image_repo.is_dirty(untracked_files=True):
        logger.info("Changes in local repository detected.")

        all_changes = []

        untracked_files = image_repo.untracked_files
        if untracked_files:
            logger.info("New untracked files:")
            for file in untracked_files:
                logger.info(file)
                all_changes.append(file)

        changed_files = image_repo.git.diff(None, name_only=True)
        if changed_files:
            logger.info("Updated files:")
            for file in changed_files.split("\n"):
                logger.info(file)
                all_changes.append(file)

        releases_list = []

        for source in updated_sources:
            for release in updated_sources[source]["releases"]:
                logger.debug("get release version data for " + source + " " + release)
                release_data = db_get_release_versions(database, source, release, 1)
                if release_data:
                    releases_list.append(
                        release_data["name"] + " " + release_data["version"]
                    )
                else:
                    logger.warn("got no release version data")

        commit_message = "Added the following releases: " + ", ".join(releases_list)
        logger.info("Commit message:")
        logger.info("%s" % commit_message)

        image_repo.git.add(all_changes)
        image_repo.index.commit(commit_message)

    try:
        image_repo.remotes.origin.push()
    except Exception as error:
        logger.error("Push into upstream repository failed %s " % error)
