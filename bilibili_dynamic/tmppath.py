import os

workpath = os.getcwd()
bsepth = f'{os.path.dirname(__file__)}/'

def set_tmp(tmp=None):
    if tmp == False:
        return False

    path = './tmp' if tmp is None else tmp
    if os.path.isabs(path):
        tmp = path
    else:
        os.chdir(workpath)
        tmp = os.path.abspath(path)
    tmp = f'{tmp}/'
    tmp_path = tmp
    pathlist = [f'{tmp_path}face/', f'{tmp_path}pendant/', f'{tmp_path}emoji/']
    for p in pathlist:
        if not os.path.isdir(p):
            os.makedirs(p)
    return tmp_path