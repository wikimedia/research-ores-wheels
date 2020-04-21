"""
Update the wheels in this repository.  This script will automatically update
the wheels in this repository after a new set of wheels were copy-pasted
into the directory.

  1. Re-checkout wheels with overlapping versions
  2. Remove old wheel versions
  3. Add new wheel versions
  4. Check if we have duplicate wheels for a given package.

Usage:
    update_wheels.py (-h | --help)
    update_wheels.py [--dry-run] [--debug]

Options:
    -h --help     Prints this documentation
    -n --dry-run  Prints the commands without running them
    --debug       Print debug logging
"""
import logging
import glob
from collections import defaultdict

import docopt

import git


logger = logging.getLogger(__name__)


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    logging.basicConfig(
        level=logging.DEBUG if args['--debug'] else logging.INFO,
        format='%(levelname)s -- %(message)s'
    )

    dry_run = args['--dry-run']

    run(dry_run)


def run(dry_run):
    repo = git.Repo(".")
    origin = repo.remote()

    # for each wheel that was overwritten, just check out the version we have.
    modified_wheels = [item.a_path for item in repo.index.diff(None)
                       if item.a_path[-4:] == ".whl"]
    for modified_wheel_path in modified_wheels:
        logger.info("Re-checking out {0}".format(modified_wheel_path))
        if not dry_run:
            origin.repo.git.checkout("origin/master", modified_wheel_path)

    # Find all of our untracked wheels.  These are new wheels.
    # We'll need to check to see if we have an old version of the file
    # and remove it.
    new_wheels = repo.untracked_files
    for new_wheel_path in new_wheels:
        package_name = new_wheel_path.split("-", 1)[0]
        package_files = glob.glob(package_name + "-*.whl")
        assert new_wheel_path in package_files, package_files
        assert len(package_files) >= 1 and len(package_files) <= 2, \
            len(package_files)

        if len(package_files) == 2:
            # There's a file to remove
            old_wheel_path = package_files[0] \
                if package_files[0] != new_wheel_path else package_files[1]
            logger.info("Removing old wheel {0}".format(old_wheel_path))
            if not dry_run:
                repo.index.remove(old_wheel_path, working_tree=True)

        logger.info("Adding new wheel {0}".format(new_wheel_path))
        if not dry_run:
            repo.index.add(new_wheel_path)

    if not dry_run:
        # Run a check that we have only one wheel per package name.
        wheels = defaultdict(list)
        for wheel_path in glob.glob("*.whl"):
            norm_package_name = wheel_path.split("-", 1)[0].lower()
            wheels[norm_package_name].append(wheel_path)

        for package_name, wheel_paths in wheels.items():
            if len(wheel_paths) > 1:
                logger.warn(
                    "Multiple wheels for the same package {0}: {1}"
                    .format(package_name, wheel_paths))


if __name__ == "__main__":
    main()
