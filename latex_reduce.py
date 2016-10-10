import re
import os


PATTERNS = dict(
    input=re.compile(r'(\s*)\\input\{([\w_\./]+)\}\s*'),
    include=re.compile(r'(\s*)\\include{([\w_\./]+)}\s*'),
    bibliography=re.compile(r'(\s*)\\bibliography{([\w_\./]+)}\s*'),
)

def reduce(src, dst):
    loc, fname = os.path.split(src)
    name, ext = os.path.splitext(fname)
    if ext not in ('.tex', ''):
        raise ValueError('file not a .tex file')

    if dst is None:
        dst = os.path.join(loc, name+'_compressed.tex')

    with open(src, 'r') as fsrc, open(dst, 'w') as fdst:
        for line in parse_file(fsrc, loc):
            fdst.write(line)


def parse_file(fh, loc):
    for line in fh:
        m = PATTERNS['input'].match(line)
        if m:
            indent, input_file = m.groups()
            yield from get_input_file(input_file, indent=indent, rootdir=loc)
            continue
        m = PATTERNS['include'].match(line)
        if m:
            indent, input_file = m.groups()
            yield from get_include_file(input_file, indent=indent, rootdir=loc)
            continue
        m = PATTERNS['bibliography'].match(line)
        if m:
            indent, input_file = m.groups()
            yield from get_bibliography_file(loc, indent=indent)
            continue
        yield line


def get_input_file(fname, rootdir, indent=''):
    fname = find_file(fname, preferred_exts=('.tex'), rootdir=rootdir)
    with open(fname, 'r') as f:
        for line in parse_file(f, rootdir):
            yield indent+line


def get_include_file(*args, **kwargs):
    yield '\\clearpage\n'
    yield from get_input_file(*args, **kwargs)


def get_bibliography_file(loc, indent=''):
    for f in os.listdir(loc):
        if os.path.splitext(f)[1] == '.bbl':
            with open(os.path.join(loc, f), 'r') as f:
                yield from f
            return
    raise IOError('could not find .bbl file')


def find_file(fname, rootdir, preferred_exts=()):
    if not os.path.isabs(fname):
        fname = os.path.abspath(os.path.join(rootdir, fname))
    if os.path.isfile(fname):
        return fname
    elif os.path.splitext(fname)[1] == '':
        for e in preferred_exts:
            if os.path.isfile(fname + e):
                return fname + e
        loc, name = os.path.split(fname)
        for itemname, ext in [os.path.splitext(f) for f in os.listdir(loc)]:
            if itemname == name:
                return fname + ext
    raise IOError('file {} not found'.format(fname))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dst')
    reduce(**vars(parser.parse_args()))
