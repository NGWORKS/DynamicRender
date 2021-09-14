import os

workpath = os.getcwd()
bsepth = os.path.dirname(__file__) + '/'

def set_tmp(tmp=None):
    if tmp == False:
        return False

    if tmp is None:
        path = './tmp'
    else:
        path = tmp

    if os.path.isabs(path):
        tmp = path
    else:
        os.chdir(workpath)
        tmp = os.path.abspath(path)
    tmp = tmp + '/'
    tmp_path = tmp
    pathlist = [tmp_path + 'face/', tmp_path + 'pendant/', tmp_path + 'emoji/']
    for p in pathlist:
        if not os.path.isdir(p):
            os.makedirs(p)
    return tmp_path