[Coming soon: installing this package directly using conda!
    For now, use the following steps to install the development
    version of this package using Git]

[DEVELOPMENT VERSION INSTALLATION STEPS]
-1. Download and install Anaconda distribution of Python 3.x:
    https://www.continuum.io/downloads

-2. Install Git, one simple option is Git For Windows:
    https://git-scm.com/downloads

-3. After setting up Git, use "git clone" to pull a copy of directory onto
    your computer, automatically set up to track shared online version.

    --Detailed Instructions--
    Open Git Bash and navigate to the directory where you want to store
    the working version of the data analysis package, e.g.
	cd ~/gitrepos/
    then type the following:
        git clone https://github.com/vsihlab/eda.git
	cd eda

-4. Use Git to check out the "develop" branch.
    Sih group members should then create a new, personal working branch
    split from the "develop" branch and maintain it online, allowing
    easy syncing between computers and facilitating the sharing of
    code fixes and improvements.

    --Detailed Instructions--
    To switch your local repository to the active development branch, type
        git checkout develop

    [for Sih group members:]
    Next, create your new branch from command line (in project folder) with:
        git checkout -b [yourname]_working_branch develop

    Finally, set up your branch to allow you to host it online via:
        git push --set-upstream origin [yourname]_working_branch

    You will need the vsihlab GitHub credentials for that step.
    e.g. "git checkout develop"
         "git checkout -b michael_working_branch develop"
         "git push --set-upstream origin michael_working_branch"

    --Further Advice--
    -A. Please see the section on version control below!
    -B. Fetch online updates and merge them before you start working,
        particularly if you've switched computers. Git makes it easy
        to keep code synced across computers, once you learn a few
        commands. Get used to typing:
            git fetch    [to check for online updates]
            git merge    [to merge online updates into current branch]
    -C. Commit file changes to your working branch ASAP, and push
        those changes to the online repository (if a Sih group member).
        This, combined with (B.), keeps code synced across computers
        and easily rolled back to previous commit.
        Also get used to this workflow:
            git status    [to list all changes]
            [for each changed file:]
                [to examine changes:] git diff [filename]
                [to keep changes:] git add [filename]
                [to revert changes:] git checkout [filename]
            [alternatively, to just add all file changes:] git add .
            git commit -m "message describing changes"
    -D. Google is your friend for Git help! But here are the most
        common commands you should probably know:
            - To swap out all files for those of another branch
              and switch to working on that branch:
                git checkout [branch name]
            - To download updates from online repository without
              actually implementing them:
                git fetch
            - To (if possible) merge in fetched updates into
              your directory without deleting any of your own changes:
                git merge
            - To see a summary of your changes since last commit
              and to see any downloaded updates relevant to your branch:
                git status
            - To confirm or "stage" changes made to a file, or
              to add a new file to the repository:
                git add [filename, or . for all files]
            - To revert all changes to a file since last commit:
                git checkout [filename]
            - To commit staged changes to the repository:
                git commit -m "[description of changes]"
            - To see changes between file and its last committed version
              (or, if changes already staged, from last staged version)
                git diff [filename]
            - To push local commits to the online repository:
                git push origin
    -E. Make use of the ability to try file versions from other people's
        branches or roll back to previous file versions on your own branch.
        Git can do anything, and again, Google is your friend.
    -F. Note: if you manage other git repositories on different git
        accounts, you may need to set repository-specific credential
        storage using the Git Credentials Manager.
        For info, check https://git-scm.com/docs/git-credential

-5. It is __strongly__ recommended you work within a virtual environment,
    which conda makes relatively painless.

    --Detailed Instructions--
    From your preferred command line tool, navigate to your local
    eda git repository and type:
	conda env create -f environment.yml

    This will install all required packages (and no others) as a virtual
    Python environment named "eda". To use it, type
	[in bash]:
	source activate eda

	[in cmd.exe]:
	activate eda

	[in Windows PowerShell]:
	cmd
	activate eda
	powershell

    This will put the text "(eda)" before the command prompt (except in
    PowerShell), letting you know you are in the virtual environment. To leave
    the environment, use the same command, except with
    "activate eda" replaced with simply "deactivate". While inside the virtual
    environment, you can run Python code with no fear of conflict with
    other installed Python packages, and without these packages affecting
    the rest of your Python install. New packages may be installed into
    your virtual environment by installing them while inside that environment,
    and they will remain local to that environment.

    Of course, command-line Python is not ideal, so you should run your
    favorite IDE from the command line:
	[To run Jupyter Notebook]:
	jupyter notebook

	[To run Spyder]:
	spyder

	[To run IDLE]:
	idle

	[To run command-line Python interpreter]:
	python

	[To run script from command-line interpreter]:
	python [script name]  (if in directory already)
	python [path-to-script]  (otherwise)

	[To install a new python package in the current environment]:
	conda install [package name]
	conda install -c [channel name, e.g. conda-forge] [package name]
	pip install

    There are ways to automate this process inside Windows shortcuts, if you
    are so inclined, but that is beyond the scope of this readme.






[ BELOW THIS LINE IS ALL OLD AND LIKELY OUTDATED ]
-----------------------------------------------------------------




VERSION CONTROL:
-Standalone scripts for personal use don't necessarily NEED to be version
    controlled at all, but any changes to the "eda"
    modules (bugfixes, added models, etc.) need to be version controlled
    both so we can benefit from each other's work and so we don't fragment
    our code base.
-To disable version control for a file, put "_nogit_" anywhere in the 
    file or folder name.
-Really, though, it can only help to keep everything under version control,
    especially for syncing between computers and sharing with others.
    Just put it in your own branch.
-Lots of git tutorials out there, I recommend learning the basics:
    "git clone", "git push/pull", "git checkout", "git commit -m 'message'",
    "git status", "git fetch/merge", "git add/rm"...it's a lot to take in,
    but extremely useful both here and in any future coding work.
-Git can get complicated, so make sure you remember to checkout a new
    branch _before_ making code changes! Working off the main branch is
    not a good idea and you don't want to have to migrate your changes
    to a separate branch later on, though anything is possible in Git
    with enough internet research.
-Git repository structure to follow the pattern at the following URL
    (it's pretty standard):
    http://nvie.com/posts/a-successful-git-branching-model/
-"Main" branch is reserved for stable versions you would trust telling
    someone to use who has no idea how the code works. If this were
    experiment running code, this is what you run
-Custom work should go on a new "feature" branch, from which some or all
    changes can be merged into the working "develop" branch which 
-"Release" branches should use "python setup.py develop" to update version
    after changing top-level "__init__.py". Don't forget CHANGES.txt either.
-Etiquette to be determined, but probably don't merge your branch into
    develop/main without talking to others. Can push your branches online
    without merging and affecting others' code, and changes to shared
    develop/main branches affect other branches downstream!


DOCUMENTATION:
-Erm, none yet. Except this readme and function docstrings.
-Paused work on implementing auto-generated documentation from the "docstrings"
    at the beginning of each python function/class/etc, using Sphinx.
    Should probably get back to that sometime.
-Note that version number is stored in top level __init__.py file
    (eda\__init__.py) as "__version__ = 'X.X.X'"
    Both Sphinx and setuptools can read this variable; only git does not
    automatically tag version numbers (or even push version tags automatically)


PACKAGE INSTALLATION [NON-ANACONDA, OUTDATED]:
-Not necessary to "install" in order to run, but doing a develop install (see
    below) allows you to run your scripts from anywhere on the computer,
    as otherwise they have to be run from the project root directory in order
    for the script to see the project modules
-Command line "python setup.py develop" - create in current python environment
    a fake package that links to the current work folder. Uninstall with
    "python setup.py develop --uninstall"
-Command line "python setup.py test" - run tests of everything in the tests
    folder using pytest. Not for installation, but great for testing!
-Command line "python setup.py install" - actually create a real install
    with a snapshot of the current work folder copied into ./lib/sitepackages
    not recommended, confuses installed version with work-in-progress version
-Note "install_requires" line of the setuptools script is borked, preventing
    an easy auto-install of required packages. Needs fixing, sorry.

IMPLEMENTATION NOTES ON ITERATORS AND ITERABLES [MOSTLY OUTDATED]:
-Most functions are set to accept iterables instead of say, lists. This means
    you can send it a list, a tuple, or even an iterator.
-Returning iterators is good practice if you can lazily process it. However,
    this can get confusing for people unfamiliar with the practice, as code
    that seems self-explanatory can fail:
        a = fcn_that_returns_iterator_instead_of_list()
        #  a = list(a) <- would fix problem, puts a's values in permanent list
        for x in a:
            print(x)  # runs fine, prints everything in a
        for x in a:
            print(x)  # _does nothing_, a is exhausted by previous loop
-In python 3.x, important built-in functions return iterators, e.g. zip()
-However, I've been moving towards returning lists instead of iterators.
    If code uses "list(fcn_returning_iterator_or_list)" everywhere it doesn't
    matter anyway, and processes like filtering tend to ruin the speedup.
    For our purposes the speed gains are unlikely to be worth the confusion.
-EXCEPTION: Parsing modules should evaluate lazily, and return iterators
    instead of lists. This is because one may want to process large amounts
    of data (e.g. a hard drive's worth), and by putting all the data in a list
    we force Python to read and store all the data at once!
    Note databrowser.py and scandatasetprocessing.py keep all data loaded at
    once, but future programs and modules by no means need to.
-RECOMMENDATION: whenever accepting a list/iterator/whatever from a function,
    use something like "returned_list = list(returned_list)" or similar
    to ensure iterators, iterables, tuples, etc. all transformed into a list.
    This means if that function is changed and the output type is modified,
    your code doesn't break. HOWEVER, despite the loss of speed, I recommend
    just returning a list rather than using fancy "yield" syntax to return
    iterators. This can be up for debate in the future.






