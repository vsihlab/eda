README: Sih Group data analysis package - development name "eda"
Last updated: 8/11/2017

[Coming soon: installing this package directly using conda!
    For now, use the following steps to install the development
    version of this package using Git]

[DEVELOPMENT VERSION INSTALLATION STEPS - WINDOWS 7+]
-1. Download and install Anaconda distribution of Python 3.x
    (available at https://www.continuum.io/downloads ), then
    install conda-build from the command line.

    --Detailed Instructions--
    From your preferred command line tool, type:
        conda update conda
        conda install conda-build
    Note: If you have trouble using Anaconda's command line tools,
          consider using the "Anaconda Prompt" installed with Anaconda.

-2. Install Git. One simple option is Git For Windows
    (available at https://git-scm.com/downloads ), as its Git Bash is a
    useful tool for using Git on Windows machines.

    You may wish to check a tutorial for some basic details on setting
    up and using Git. While we will be using GitHub instead of BitBucket
    as our online repository, the latter's website is still an extremely
    informative source, and 99+% of it still applies to our usage:
    https://www.atlassian.com/git/tutorials/install-git#windows

    In particular, make sure to set up your credentials.
    e.g. in Git Bash, type:
        git config --global user.name "Your Name Comes Here"
        git config --global user.email you@yourdomain.example.com

-3. After setting up Git, use "git clone" to pull a copy of directory onto
    your computer, automatically set up to track shared online version.

    --Detailed Instructions--
    Open Git Bash and navigate to the directory where you want to store
    the working version of the data analysis package. Note that
    for Windows, ~ translates to C:/Users/[current user]
    examples:
	cd ~/gitrepos/
        cd ///c/source/repos/
        [etc.]
    then type the following:
        git clone https://github.com/vsihlab/eda.git
	cd eda

-4. Use Git to check out the best branch for your purposes.
    - "master" for optimal stability, such as for production code.
    - "develop" for the most current build but with potential bugs.
    If you plan to edit or add any code in the package, and
    __as an alpha release you probably will need to__, it is strongly
    recommended you create a new, personal working branch split from
    the "develop" branch to allow version-controlled editing.
    Furthermore, Sih group members can maintain these online, allowing
    easy syncing between computers and facilitating the sharing of
    code fixes and improvements.
    Other folks are free to fork the repository, of course!

    --Detailed Instructions--
    To switch your local repository to any given branch, use the
    "git checkout" command in the Git Bash (while in the repository).
    For example, to switch to the latest release ("master" branch), type:
        git checkout master
    Whereas to switch to the active development branch ("develop"), type:
        git checkout develop
    To create and switch to your own working branch off develop, type:
        git checkout -b [yourname]_working_branch develop

    [for Sih group members:]
    Set up your branch online for easy syncing and sharing via:
        git push --set-upstream origin [yourname]_working_branch
    You will need the vsihlab GitHub credentials for this step.

    --Further Advice--
    90% of your git usage will be the same small set of commands,
    all in your own working branch, and the rest can be done with
    the guidance of the repository maintainer. As such, it's not
    necessary for everyone to understand everything about Git.
    Here are the most important things you should know:
    -A. Good sources of information:
        - The version control section later in this readme
        - [reference/tutorials]
            -[simple beginner's intro]
                http://rogerdudler.github.io/git-guide/
            -[cheatsheet, and site full of tutorials]
                https://www.atlassian.com/git/tutorials/atlassian-git-cheatsheet
        - ["gitflow" workflow explanations]
            -[original outline]
                http://nvie.com/posts/a-successful-git-branching-model/
            -[alternate explanation]
                https://www.atlassian.com/git/tutorials/comparing-workflows#gitflow-workflow
    -B. Fetch online updates and merge them before you start working,
        particularly if you've switched computers. Git makes it easy
        to keep code synced across computers, once you learn a few
        commands. Get used to typing:
            git fetch    [to check for online updates]
            git merge    [to merge online updates into current branch]

        Periodically you will want to merge in changes others have
        made to the develop branch into your working branch as well.
        Unless there is a direct conflict, it will be instant:
            git merge develop
    -C. Commit file changes to your working branch ASAP, and always
        immediately push those changes to the online repository.
        This, combined with (B), keeps code synced across computers
        and easily rolled back to previous commit.
        Get used to this workflow:
            git status    [to list all changes]
            [to add all file changes:] git add .
            [OR, for each changed file -]
                [- to examine changes:] git diff [filename]
                [- to keep changes:] git add [filename]
                [- to revert changes:] git checkout -- [filename]
            git commit -m "message describing changes"
            git push origin
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

-5. Create a virtual environment for using this development package
    using the environment.yml in the git repository to install
    all prerequisites. It is __strongly__ recommended you work within
    a virtual environment for Python work in general, and Anaconda makes
    this process relatively painless.

    --Detailed Instructions--
    From your preferred command line tool, navigate to your local
    eda git repository and type:
	conda env create -n eda-dev -f environment.yml

    This will install all required packages (and no others) as a virtual
    Python environment named "eda-dev", but feel free to substitute that
    name with any other name you prefer, just substitute "eda-dev" with
    your name of choice in all code examples.
    __Do not activate this virtual environment yet__

-6. Finally, install the package repository into your virtual
    environment in "development mode" by using conda-build's
    conda-develop command. 

    --Detailed Instructions--
    From your preferred command line tool, navigate to your local
    eda git repository and type the following while NOT within
    any virtual environment:
        conda-develop . -n eda-dev

-7. Installation complete. Run Python from within the virtual
    environment you created in order to use the development version
    of this package. This means that conda will treat the
    git repository as an installed package, allowing use from
    any location on the computer. Also, changes to the repository,
    such as checking out a different git branch, will immediately
    affect code run in this virtual environment, though edited
    modules will need to be reloaded if already imported in
    order for changes to take effect. In Jupyter, it is perhaps
    easiest to just reload the kernel.

    Sih group members, please take note of the version control
    advice further down in this readme.

    Of course, command line Python is not ideal, so you should
    run your favorite IDE from the command line, which will give
    you the usual visual interface but with the custom Python
    installation of the virtual environment.

    --Detailed Instructions--
    To activate your virtual environment, type:
	[in bash]:
	source activate eda-dev

	[in cmd.exe]:
	activate eda-dev

	[in Windows PowerShell]:
	cmd
	activate eda-dev
	[to regain PowerShell functionality:] powershell

    This will put the text "(eda)" before the command prompt (except in
    PowerShell), letting you know you are in the virtual environment.
    To leave the environment, use the same command, except with
    "activate eda" replaced with simply "deactivate". While inside the
    virtual environment, you can run Python code with no fear of conflict
    with other installed Python packages, and without these packages
    affecting the rest of your Python install.

    There are ways to automate this process inside Windows shortcuts and
    thus removing the command line requirement, if you are so inclined,
    but that is beyond the scope of this readme.

    Useful tools installed as part of this package's prerequisites:
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

	[To install a new python package]:
	conda install [package name]
	conda install -c [channel name, e.g. conda-forge] [package name]
	pip install

    Note there is no reason you need use the exact version numbers
    specified in the environment.yml file; these are just known versions that
    seem to reliably avoid any errors with the installation of numpy, which
    sometimes fails with certain package version combinations. Packages can
    be updated and new packages may be installed into your virtual environment
    by normal command line methods while inside the virtual environment,
    and these updates/installations will remain local to that environment.
    Alternatively, you can edit the environment.yml file to your liking before
    creating your virtual environment from it, so that others can repeat
    your process by using your environment.yml.

[NOTES ON USING JUPYTER NOTEBOOK]
[in development]
-1. First, you will want to make sure nbconfigurations is correctly
    installed - in your virtual environment, type in the command line:
        jupyter nbextension enable --py widgetsnbextension

-2. You may want to customize your jupyter's look using jupyter-themes,
    for example to create light text on a dark background, or to change
    the default features of plots to make them fit the style of your
    presentation or journal article. See the official GitHub repository
    for jupyter-themes for details:
        https://github.com/dunovank/jupyter-themes

[NOTES ON VERSION CONTROL]
-A. Recreating old code environments is the best feature that Git
    and conda provide, ensuring old code will always remain usable.
    To take advantage, ALWAYS put a comment at the top of your code
    noting the exact version number / working branch commit ID used
    to run it. This way, you can always run old notebooks/scripts by
    reverting your git repo to that version and creating a new
    virtual environment from the environment.yml therein, following
    the development version installation steps 4-6 above.
    If using additional packages, consider creating a custom
    environment.yml to keep with the script/notebook to use instead.
-B. I can't stress enough - Google is your friend. Whatever you need
    to do, someone on Stack Exchange or elsewhere has instructions
    for doing it.
-C. Try to keep the repository set to your own working branch, and
    make sure to use "git fetch" and "git merge" regularly to merge
    in fixes and new content from the shared develop branch, as well
    as syncing in commits you may have pushed from other computers.
-D. Standalone scripts/notebooks for personal use don't necessarily
    NEED to be version controlled at all, but any changes to the "eda"
    modules (bugfixes, added fit/simulation models, etc.) need to be
    version controlled both so we can benefit from each other's work
    and so we don't fragment our code base.
-E. To version control your own files (scripts, notebooks, etc.), you'll
    probably want create your own git repository in whatever folder they
    are in, which is easily done offline simply by typing "git init" into
    Git Bash while inside that folder - that's all it takes.
    However, Sih group members may also want to share/sync some notebooks
    by saving them in the package repository and commiting them to their
    own working branch.
-E. To disable version control for a file stored in the repository, put
    "_nogit_" anywhere in the file or folder name.
-F. Sih group members: to integrate individual fixes into the shared
    development branch and to push out stable releases, we follow the
    "Gitflow" repository model explained at the following URL:
    http://nvie.com/posts/a-successful-git-branching-model

    Another explanation with pictures and examples can be found here:
    https://www.atlassian.com/git/tutorials/comparing-workflows#gitflow-workflow

    Summaries of this git repo style:
    -1. "Master" branch is reserved for trusted, stable versions.
        This should only consist of mostly bug-free (hopefully) releases
        approved by the git repository's maintainer.
        NOTE: Production code (e.g. used to create journal article
        figures) should probably be run only from this branch, so
        that it can be reliably reproduced by anyone with the data
        simply by installing the proper version.
    -2. "Develop" branch should be a mostly stable version that
        implements all the newest fixes and features that seem to
        avoid breaking anything, but aren't yet well-tested enough
        for official release.
    -3. UNIQUE TO THIS REPOSITORY: "Working" branches for Sih group
        members. Lets you sync your jumbles of ad hoc changes and
        hotfixes between computers without immediately worrying about
        sorting and implementing them. But most fixes/changes/additions
        should eventually be isolated and turned into feature branches:
    -4. "Feature" branches contain all the changes you make that you
        want to share with others, and with the maintainer's blessing
        they can be merged into the "develop" branch and thus
        automatically merged into everyone's individual working branches
        for immediate use.
    -5. "Release" branches periodically take the tried-and-true updates
        from the "develop" branch, update the release version number
        in CHANGES.txt and /eda/__init__.py, and then are merged into
        the master branch as a stable release.
-H. While it's easy for everyone to just go their own way forever,
    as people find bugs and add features it is important that group
    members share their improvements by extracting them to feature
    branches for sharing with others. For help here, contact the
    current maintainer of the Git repository. But the gist is that
    you check out a new feature branch off develop, then import
    the new and/or changed files from your own working branch:
        git checkout -b [new feature branch name] develop
        [for each new/changed file to share:]
            git checkout [your working branch name] -- [filename]
        git add .
        git commit -m "extracted changes from working branch"
    Then you can work with the repository maintainer to decide what
    changes, if any, need to be made before rolling the feature
    branch into the shared develop branch.
-I. Etiquette is yet to be determined, but probably don't merge your
    working or feature branches into develop/main without talking to
    the repository maintainer.
    NOTE: If you commit notebooks to the shared repository, even on your
          own working branch, please avoid large file/image sizes to avoid
          repository size bloat for everyone. This is NOT a problem if you
          create a separate personal repository elsewhere with "git init".
          So if you normally create large figures with a command like
              plt.figure(figsize=(12,8))
          Consider replacing such commands with something like
              plt.figure(figsize=WIDE_FIGURE_SIZE)
          where WIDE_FIGURE_SIZE is a global variable that can be
          easily changed at the start of the notebook to generate
          smaller figures before saving to the shared repository.
          e.g. at the top of the notebook:
              # WIDE_FIGURE_SIZE = (12, 8)  # normal use (commented out)
              WIDE_FIGURE_SIZE = (4, 3)  # small version for shared repo
          See the /examples directory for notebooks that do this.






