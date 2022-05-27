import os, sys
from git import Repo
from github import Github
import logging
import uc_migration_utils as ucutil


SOUP_PARSER = "lxml" #"html.parser"
script_name = "add_to_git_from_local_repo"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log")
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(script_name)


logger1.addHandler(fh)
logger1.addHandler(ch)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def main():
    config = ucutil.get_config()
    
    repo_dir =config[ucutil.LOCAL_DOCREPO_LOCATION]
    logger1.info (f"Repo-dir={repo_dir}")
    repo = Repo(repo_dir)    
    
    rootdir=ucutil.get_target_doc_path(config, "", level=ucutil.DOC_LEVEL_PLUGIN_README)
    logger1.info(f"Rootdir={rootdir}")
    for subdir, dirs, files in os.walk(rootdir):
        logger1.info(f"subdir={subdir}")
        # 
        dir_parts=subdir.split("/")
        for file in files:
            logger1.info(f"file={file}")
            if (".DS_Store" in file): continue
            rval = ""
            logger1.info(f"adding {subdir}/{file}")
            rval = repo.git.add(f"{subdir}/{file}")
            logger1.info (f"add-return={rval}")
        
        # debug
        
        logger1.info(f"adding folder {dir_parts[-1]}")
        try:    
            rval = repo.index.commit(f"adding {dir_parts[-1]}")
            logger1.info (f"commit-return={rval}")
            origin = repo.remote("origin")
            rval = origin.push().raise_if_error()
            logger1.info (f"push-return={rval}")

        except Exception as ex:
            logger1.exception(f"Exception {ex} occured during add,commit or push of file: {file}")
            os.exit(0)
    
if __name__ == '__main__':
    main()    