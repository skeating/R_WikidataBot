__author__ = 'Sarah Keating'

global server
server = 'www.wikidata.org'

global used_wd_ids
used_wd_ids = dict({'pmid': [], 'goterms': [], 'reactome': []})

global supported_properties
supported_properties = [{'id': 'P686', 'name': 'goterm'},
                        {'id': 'P3937', 'name': 'reactomeid'},
                        {'id': 'P698', 'name': 'pmid'},
                        {'id': 'P352', 'name': 'uniprotid'}
]

global supported_species
supported_species = [dict({'ReactomeCode': 'HSA', 'name': 'Homo sapiens', 'WDItem': 'Q15978631'})]

global edited_wd_pages
edited_wd_pages = []
