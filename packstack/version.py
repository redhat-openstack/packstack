
VERSION = ['2014', '1', '1']
FINAL=False
RELEASE="Icehouse"
SNAPTAG=None

def release_string():
    return RELEASE

def version_string():
    if FINAL:
        return '.'.join(filter(None, VERSION))
    else:
        return '.'.join(filter(None, VERSION))+"dev{0}".format(SNAPTAG)
