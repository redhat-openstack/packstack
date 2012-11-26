
VERSION = ['2013', '2', '1']
FINAL=False

def version_string():
    if FINAL:
        return '.'.join(filter(None, VERSION))
    else:
        return '.'.join(filter(None, VERSION))+"dev"
        

