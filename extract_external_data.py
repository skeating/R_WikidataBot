__author__ = 'Sarah'

class ExtractExternalData:
    def __init__(self, data_type):
        self.data_type = data_type
        self.data = []

        self.supported_data = [{'datatype': 'psimod', 'datafile': './ontology_data/psimod_obo.txt'},
            {'datatype': 'PRO', 'datafile': './ontology_data/pro_ref.csv'}]

    def populate_data(self):
        filename = self.get_data_file()
        if not filename:
            return
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        if self.data_type == 'psimod':
            self.get_psimod_terms(lines)
        elif self.data_type == 'PRO':
            self.get_pro_data(lines)

    def get_data(self):
        return self.data

    def get_data_file(self):
        for data in self.supported_data:
            if data['datatype'] == self.data_type:
                return data['datafile']
        return None

    def get_psimod_terms(self, lines):
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

    def get_pro_data(self, lines):
        for line in lines:
            if line.endswith('\n'):
                length = len(line)
                line = line[0:length-1]
            vars = line.split(',')
            if len(vars) < 2:
                continue
            term = dict({'id': vars[0], 'pro': vars[1]})
            if term:
                self.data.append(term)



