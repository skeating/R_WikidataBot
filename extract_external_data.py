__author__ = 'Sarah'

import sys

class ExtractExternalData:
    def __init__(self, data_type):
        self.data_type = data_type
        self.data = []

        self.supported_data = [{'datatype': 'psimod', 'datafile': './ontology_data/psimod_obo.txt'}]

    def populate_data(self):
        filename = self.get_data_file()
        if not filename:
            return
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        self.get_terms(lines)

    def get_data(self):
        return self.data

    def get_data_file(self):
        for data in self.supported_data:
            if data['datatype'] == self.data_type:
                return data['datafile']
        return None

    def get_terms(self, lines):
        for i in range(0, len(lines)):
            if not lines[i].startswith('[Term]'):
                continue
            else:
                if self.data_type == 'psimod':
                    term = self.get_psimod_term(lines, i)
                    if term:
                        self.data.append(term)
                    i += 3

    def get_psimod_term(self, lines, i):
        nextline = lines[i+1]
        length = len(nextline)
        id = nextline[4:length-1]

        nextline = lines[i+2]
        length = len(nextline)
        name = nextline[6:length-1]

        nextline = lines[i+3]
        start = nextline.find('ChEBI:')
        chebi = ''
        if start != -1:
            comma = nextline.find(',', start)
            chebi = nextline[start+6: comma]

        if chebi != '':
            term = dict({'id': id, 'name': name, 'chebi': chebi})
            return term
        else:
            return None


