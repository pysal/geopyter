import nbformat
import io

try:
    xrange
except:
    xrange = range


def read_nb(nb, ext=True):
    """
    Read a notebook file and return a notebook object.

    Parameters
    ==========
    nb: String
        Path to the notebook file; if the path does not end
        in '.ipynb' then this will be appended unless you
        override this by setting the 'ext' to False.
    ext: boolean
        Defaults to True, meaning that the '.ipynb'
        extension will be automatically added. If you do not
        want this behaviour for some reason then set ext to False.

    Returns
    =======
    An object of class nbformat.notebooknode.NotebookNode
    """

    # Append file extension if missing and ext is True
    if not nb.endswith('.ipynb') and ext is True:
        nb += '.ipynb'

    # Read-only in UTF-8, note NO_CONVERT.
    with io.open(nb, 'r', encoding='utf8') as f:
        nb = nbformat.read(f, nbformat.NO_CONVERT)

    return nb

def write_nb(nb, fn):
    """
    Write a notebook to the path specified.

    Parameters
    ==========
    nb: nbformat.notebooknode.NotebookNode
        A notebook object to write to disk.
    fn: String
        Path to which you want the notebook written. _Note:_
        for simplicity's sake this will automatically append
        '.ipynb' to the filename; however we recommend that
        you not get lazy and rely on this feature since it may
        go away in the future.

    Returns
    =======
    Void.
    """

    # Append file extension
    if not fn.endswith('.ipynb'):
        fn += '.ipynb'

    # Write raw notebook content
    with io.open(fn, 'w', encoding='utf8') as f:
        nbformat.write(nb, f, nbformat.NO_CONVERT)

from collections import defaultdict
def get_nb_structure(nb):
    cell_types = defaultdict(list)
    for i, cell in enumerate(nb['cells']):
        cell_types[cell.cell_type].append(i)
    return cell_types

def dump_nb(nb, cells=5, lines=5):
    """
    Dump content of a notebook to STDOUT to aid in debugging.

    Parameters
    ==========
    nb: nbformat.notebooknode.NotebookNode
        A notebook object from which to dump content.
    cells: int
        Select an arbitrary number of cells to output. Defaults to 5.
    lines: int
        Select an arbitrary number of lines from each cell to output. Defaults to 5.

    Returns
    =======
    Void.
    """

    # For the cell-range specified
    for c in xrange(0, cells):

        # Check we still have cells to read
        if c < len(nb.cells):

            # And dump the contents to STDOUT
            print("====== " + nb.cells[c]['cell_type'] + " ======")
            src = nb.cells[c]['source'].splitlines()
            if len(src) > lines:
                print('\n'.join(src[0:lines]))
                print("...")
            else:
                print(nb.cells[c]['source'])


from git import Repo

def gitter(path='.'):
    """
    Try to collect GitHub information to use in tracking
    authorship contributions and allow specification of
    particular versions of notebooks.

    Parameters
    ==========
    path: String
        The path to a GitHub repository. Defaults to '.'

    Returns
    =======
    rp: dict
        A dictionary containing relevant git metadata
    """
    repo = Repo(path)

    rp = {}

    rp['active_branch'] = str(repo.active_branch)

    hc = repo.head.commit
    rp['author.name'] = hc.author.name
    rp['authored_date'] = datetime.datetime.fromtimestamp(hc.authored_date).strftime('%Y-%m-%d %H:%M:%S')
    rp['committer.name'] = hc.committer.name
    rp['committed_date'] = datetime.datetime.fromtimestamp(hc.committed_date).strftime('%Y-%m-%d %H:%M:%S')
    rp['sha'] = hc.hexsha

    return rp

import re
import importlib
def find_libraries(nb):
    """
    Utility function to find libraries imported by notebooks
    and assemble them into a group for reporting and testing
    purposes.

    Parameters
    ==========
    nb: nbformat.notebooknode.NotebookNode
        A notebook object to search for import statements

    Returns
    =======
    libs: Set
        A set containing the libraries imported by the notebook
    """

    # Find and classify the cells by type [code, markdown]
    cell_types = get_nb_structure(nb)

    libs  = set()
    vlibs = {}

    # Iterate over the code cell-types
    for c in cell_types['code']:
        try:
            #print("-" * 25)
            #print(nb.cells[c]['source'])

            # Convert the code into a block of lines
            block = nb.cells[c]['source'].splitlines()
            # Loop over the lines looking for import-type statements
            for l in block:
                m = re.match("(?:from|import) (\S+)", l)
                if m:
                    libs.add(m.group(1))
        except IndexError: #Catch index error (not sure where this comes from)
            pass

    # Try to get the versions in use on the machine
    for l in libs:
        l = l.split('.')[0]
        #print("Checking version of " + l)
        mod = importlib.import_module(l)
        ver = None
        try:
            ver = mod.__version__
        except AttributeError:
            try:
                ver = mod.version
            except AttributeError:
                print("Unable to determine version for: " + l)
                print("Currently we check <module>.__version__ and <moduled>.version")
                pass
        vlibs[l] = ver
    return vlibs

def write_metadata(nb, nm, val, namespace=u'geopyter'):
    """
    Add or append metadata values to the geopyter parameter.

    Parameters
    ==========
    nb: nbformat.notebooknode.NotebookNode
        A notebook object to which to add Geopyter metadata.
    nm: String
        The name of the key within the Geopyter dictionary that we want to update.
    val: String, List, Dictionary
        The value to associate with the key.

    Returns
    =======
    Void.
    """

    # Check for the namespace in the notebook metadata
    if not namespace in nb.metadata:
        nb.metadata[namespace] = {}

    # And write it
    nb.metadata[namespace][nm] = val


def get_metadata(nb, nm, namespace=u'geopyter'):
    """
    Retrieve metadata values from the geopyter parameter.

    Parameters
    ==========
    nb: nbformat.notebooknode.NotebookNode
        A notebook object to which to add Geopyter metadata.
    nm: String
        The name of the key within the Geopyter dictionary that we want to retrieve.

    Returns
    =======
    Void.
    """

    # Check for the namespace in the notebook metadata
    if not nb.metadata.has_key(namespace):
        nb.metadata[namespace] = {}

    # And write it
    nb.metadata[namespace][nm] = val


def read_user_metadata(nb):
    src = nb.cells[0]['source']
    #print(src)

    meta = {}

    if not re.match("\# \w+", src):
        print("The first cell should be of level h1 and contain a bulleted list of metadata.")

    for l in src.splitlines():
        m = re.match("- ([^\:]+?)\: (.+)", l)
        if m is not None:
            val = m.group(2).split(';')
            if len(val)==1:
                val = val[0]
            meta[m.group(1)] = val

    return meta


from collections import defaultdict
def get_structure(cells):
    cell_types = defaultdict(list)
    for i, cell in enumerate(cells):
        cell_types[cell.cell_type].append(i)
    return cell_types


def remove_outputs(nb):
    """Set output attribute of all code cells to be empty"""
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []

def clear_notebook(old_ipynb, new_ipynb):
    with io.open(old_ipynb, 'r') as f:
        nb = nbformat.read(f, nbformat.NO_CONVERT)

    remove_outputs(nb)

    with io.open(new_ipynb, 'w', encoding='utf8') as f:
        nbformat.write(nb, f, nbformat.NO_CONVERT)


import re
"""
import markdown
from bs4 import BeautifulSoup

md = markdown.Markdown()

cell_types = get_nb_structure(nb)

# Iterate over the code cell-types
for c in cell_types['markdown']:

    # Delete code blocks -- this is a bit brutal
    # and it might be better to escape them in some
    # way... but this at least works well enough
    src = re.sub(r'```.+?```', '', nb.cells[c]['source'], flags=re.S)

    print("-"*20 + "New Cell" + "-"*20)
    soup = BeautifulSoup(md.convert(src), 'html.parser')

    h1 = soup.findAll('h1')
    print( ", ".join([x.contents[0] for x in h1]))

    h2 = soup.findAll('h2')
    print( ", ".join([x.contents[0] for x in h2]))

    h3 = soup.findAll('h3')
    print( ", ".join([x.contents[0] for x in h3]))
"""

class NoteBook(object):
    def __init__(self, ipynb):
        self.nb = read_nb(ipynb)
        self.structure = self.get_structure()

    def get_structure(self):
        cell_types = defaultdict(list)
        for i, cell in enumerate(self.nb.cells):
            cell_types[cell.cell_type].append(i)
        return cell_types

    def get_cells_by_type(self, cell_type=None):
        if cell_type:
            cell_type = cell_type.lower()
            return [self.nb.cells[i] for i in self.structure[cell_type]]
        else:
            return self.nb.cells

    def get_cells_by_id(self, ids=[]):
        return [self.nb.cells[i] for i in ids]

    def get_header_cells(self):
        rh1 = re.compile('(?<!#)# ')
        rh2 = re.compile('(?<!#)## ')
        rh3 = re.compile('(?<!#)### ')
        rh4 = re.compile('(?<!#)#### ')
        rhs = rh1, rh2, rh3, rh4
        hs = {1:[], 2:[], 3: [], 4: []}
        idxs = self.structure['markdown']
        cells = self.get_cells_by_id(idxs)
        pairs = zip(idxs, cells)
        for idx, cell in pairs:
            source = cell['source']
            # Delete code blocks -- this is a bit brutal
            # and it might be better to escape them in some
            # way... but this at least works well enough
            source = re.sub(r'```.+?```', '', source, flags=re.S)
            for j, rh in enumerate(rhs):
                fa = rh.findall(source)
                if fa:
                    for match in fa:
                        hs[j+1].append(idx)
        return hs

    def get_tree(self):
        tree = []
        levels = range(4, 1, -1)
        h_cells = self.get_header_cells()
        for level in levels:
            children = h_cells[level]
            parents = []
            for child in children:
                parent_level = level - 1
                while parent_level > 0:
                    candidates = [parent for parent in h_cells[parent_level]]
                    parents.extend([c for c in candidates if c < child])
                    parent_level -= 1

                parent = max(parents)
                tree.append([parent, child])
        return tree
