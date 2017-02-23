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

class Cell(object):
    """docstring for Cell"""
    def __init__(self, nb,  idx):
        #super(Cell, self).__init__()
        self.nb = nb
        self.idx = idx
        if self.is_include():
            self.cell_type='include'
        else:
            self.cell_type = self.nb.cells[idx].cell_type

    def is_include(self):
        """determine if this is an include cell"""
        if "@include" in self.nb.cells[self.idx].source:
            return True
        return False

    def source(self):
        return self.nb.cells[self.idx].source

    def set_metadata(self, val, nm=None, namespace='geopyter'):

        if namespace is None:
            self.nb.cells[self.idx].metadata[nm] = val

        else:
            # Check for the namespace in the notebook metadata
            if namespace not in self.nb.cells[self.idx].metadata:
                self.nb.cells[self.idx].metadata[namespace] = {}

            if nm is None:
                self.nb.cells[self.idx].metadata[namespace] = val
            else:
                self.nb.cells[self.idx].metadata[namespace][nm] = val

import re
import nbformat
import importlib
from git import Repo
from git import InvalidGitRepositoryError
from collections import defaultdict
from datetime import datetime
import os
class NoteBook(object):
    def __init__(self, ipynb):
        self.nb = read_nb(ipynb)
        self.nb_path = ipynb
        self.cells = []

        cell_types = defaultdict(list)
        for i, c in enumerate(self.nb.cells):
            cell = Cell(self.nb, i)
            cell.set_metadata(self.get_user_metadata().copy())
            cell.set_metadata(nm='git', val=self.get_git_metadata().copy())
            self.cells.append(cell)
            cell_types[cell.cell_type].append(i)
        self.structure = cell_types
        self.set_metadata(self.get_user_metadata())
        self.set_metadata(nm='libs', val=self.get_libs())

    def write(self, fn=None):
        """
        Write a notebook to the path specified.

        Parameters
        ==========
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

        if fn is None:
            fn = re.sub('(\.ipynb)$','-compiled', self.nb_path)

        # Append file extension
        if not fn.endswith('.ipynb'):
            fn += '.ipynb'

        # Write raw notebook content
        with io.open(fn, 'w', encoding='utf8') as f:
            nbformat.write(self.nb, f, nbformat.NO_CONVERT)

    def structure(self):
        return self.structure

    def get_cells_by_type(self, cell_type=None):
        if cell_type:
            cell_type = cell_type.lower()
            return [self.cells[i] for i in self.structure[cell_type]]
        else:
            return self.cells

    def get_cells_by_id(self, ids=[]):
        return [self.cells[i] for i in ids]

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
            #source = cell['source']
            source = cell.source()
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

    ###########################
    # Metadata-related functions
    ###########################
    def get_metadata(self, nm=None, namespace=u'geopyter'):
        """
        Retrieve metadata values from the metadata of a Jupyter notebook. Works with
        an object of type nbformat.notebooknode.NotebookNode.

        Parameters
        ==========
        namespace: String
            The name of the 'namespace' within the notebook metadata that
            we want to read. Defaults to 'geopyter' so that we only look
            within 'our' dictionary of metadata values. Set to None if you
            want to retrieve Jupyter metadata values.
        nm: String
            The name of the metadata that we want to retrieve.
            Defaults to None with a view to returning everything contained in the namespace

        Returns
        =======
        Void.
        """

        if namespace is None and nm is None:
            # If the namespace has been deliberately set to None
            # then return all of the notebook's metadata
            return self.nb.metadata
        elif namespace is None and self.nb.metadata.has_key(nm):
            # Return a value from the notebook's metadata store
            return self.nb.metadata[nm]
        elif not self.nb.metadata.has_key(namespace):
            # If the namespace doesn't exist then return None
            return None
        elif nm is None:
            # If the name is set to None then return the whole namespace
            return self.nb.metadata[namespace]
        else:
            # Otherwise, return exactly what was requested
            return self.nb.metadata[namespace][nm]

    def set_metadata(self, val, nm=None, namespace=u'geopyter'):
        """
        Write metadata values to the metadata of a Jupyter notebook. Works with
        an object of type nbformat.notebooknode.NotebookNode.

        Parameters
        ==========
        namespace: String
            A 'namespace' into which to write the metadata value. Defaults to
            'geopyter' to keep you from trampling on Jupyter's metadata, but
            can be set to None if you need to modify non-geopyter values.
        nm: String
            The name of the key within the Geopyter dictionary that we want to update.
        val: String, List, Dictionary
            The value to associate with the key.

        Returns
        =======
        Void.
        """

        if namespace is None:
            self.nb.metadata[nm] = val

        else:
            # Check for the namespace in the notebook metadata
            if namespace not in self.nb.metadata:
                self.nb.metadata[namespace] = {}

            if nm is None:
                self.nb.metadata[namespace] = val
            else:
                self.nb.metadata[namespace][nm] = val

    def get_user_metadata(self):
        """
        Read 'user'-specified (i.e. content-developer specified) metadata from
        the first cell of the notebook. The first cell in an included notebook
        should contain only the title (header level 1 = #) and then an unordered
        markdown list of metadata values in the form: `key: value; value; ...`
        (see Documentation).

        Parameters
        ==========
        None.

        Returns
        =======
        meta: dict
            A dictionary of key value pairs to be used as metadata in tracking content contributions.
        """
        # Initialise the user_metadata attribute if it doesn't exist
        if not hasattr(self, 'user_metadata'):

            # Retrieve the source from the first cell
            src = self.nb.cells[0]['source']

            meta = {}

            content = ""

            # Try to parse it -- warn the user (but don't die) if
            # we can't make sense of what we're seeing.
            if not re.match("\# \w+", src):
                print("The first cell should be of level h1 and contain a bulleted list of metadata.")
            else:
                # In the future it might be a good idea to make this
                # check a little smarter (e.g. to allow other types of
                # content in the first cell) but this will do for now.
                for l in src.splitlines():
                    m = re.match("(?:\-|\*|\d+)\.? ([^\:]+?)\: (.+)", l)
                    if m is not None:
                        try:
                            val = map(unicode.strip, m.group(2).split(';'))
                        except:
                            val = [ s.strip() for s in m.group(2).split(';')]

                        if len(val)==1:
                            val = val[0]
                        meta[m.group(1)] = val
                    else:
                        content += l + "\n"
                self.user_metadata = meta.copy()
                self.nb.cells[0]['source'] = content

        return self.user_metadata

    def get_git_metadata(self, repo_path=None):
        """
        Try to collect GitHub information to use in tracking
        authorship contributions and allow specification of
        particular versions of notebooks.

        Parameters
        ==========
        path: String
            The path to a GitHub repository. Defaults to '.', but normally
            called with the path of the currently-being-parsed notebook.

        Returns
        =======
        rp: dict
            A dictionary containing relevant git metadata
        """
        if not hasattr(self, 'repo'):

            if repo_path is None:
                repo_path = self.nb_path

            # A process that looks progressively further up the diretory
            # tree until it finds a repo.
            while not os.path.exists(os.path.join(repo_path,'.git')):
                repo_path = os.path.dirname(repo_path)

            # Throws InvalidGitRepositoryError if a .git directory
            # could be found in the recursion process above.
            repo = Repo(repo_path)

            rp = {}

            rp['active_branch'] = str(repo.active_branch)

            hc = repo.head.commit
            rp['author.name'] = hc.author.name
            rp['authored_date'] = datetime.fromtimestamp(hc.authored_date).strftime('%Y-%m-%d %H:%M:%S')
            rp['committer.name'] = hc.committer.name
            rp['committed_date'] = datetime.fromtimestamp(hc.committed_date).strftime('%Y-%m-%d %H:%M:%S')
            rp['sha'] = hc.hexsha

            self.repo = rp.copy()

        return self.repo

    def get_libs(self):
        """
        Try to find all libraries imported by this notebook
        and assemble them into a group for reporting and testing
        purposes. Works with the Jupyter notebook class to search
        the source for import statements.

        Parameters
        ==========
        None.

        Returns
        =======
        libs: dict
            A dict containing the libraries imported by the notebook and their
            versions.
        """
        if not hasattr(self, 'libs'):
            libs  = set() # All unique libraries used
            vlibs = {} # Versioned libraries

            # Iterate over the code cell-types
            for c in self.structure['code']:
                try:
                    # Convert the code into a block of lines
                    block = self.cells[c].source().splitlines()
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
                        print("Currently we check <module>.__version__ and <module>.version")
                        pass
                vlibs[l] = ver
            self.libs = vlibs.copy()

        return self.libs
