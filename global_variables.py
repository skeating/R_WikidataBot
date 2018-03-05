__author__ = 'Sarah Keating'

global server
server = 'www.wikidata.org'

global used_wd_ids
used_wd_ids = dict({'pmid': [], 'goterms': [], 'reactome': [], 'chebi': [], 'proteins': []})

global supported_properties
supported_properties = [{'id': 'P686', 'name': 'goterm'},
                        {'id': 'P3937', 'name': 'reactomeid'},
                        {'id': 'P698', 'name': 'pmid'},
                        {'id': 'P352', 'name': 'uniprotid'},
                        {'id': 'P683', 'name': 'chebi'}
]

global supported_species
supported_species = [dict({'ReactomeCode': 'HSA', 'name': 'Homo sapiens', 'WDItem': 'Q15978631'})]

global edited_wd_pages
edited_wd_pages = []

global exceptions
exceptions = []

global psimod
psimod = []

global prodata
prodat = []

def set_psimod(data):
    global psimod
    psimod = data

def set_prodata(data):
    global prodata
    prodata = data

def get_chebi_from_mod(modref):
    if len(psimod) == 0:
        return ''
    else:
        for ref in psimod:
            if ref['id'] == modref:
                return ref['chebi']
    return ''

def get_pro_for_id(id):
    if len(prodata) == 0:
        return ''
    else:
        for ref in prodata:
            if ref['id'] == id:
                return ref['pro']
    return ''
