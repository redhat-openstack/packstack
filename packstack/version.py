
VERSION = ['2012', '2', '3']
FINAL=False

def version_string():
    if FINAL:
        return '.'.join(filter(None, VERSION))
    else:
        return '.'.join(filter(None, VERSION))+"dev"
        

