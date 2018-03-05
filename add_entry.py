__author__ = 'Sarah'

import acquire_wikidata_links
import global_variables
from wikidataintegrator import wdi_core
import copy
from time import gmtime, strftime


class AddEntry:
    """
    class to create the set of data for a base wikidata entry
    """
    def __init__(self, reactome_id, wd_sparql, reference, species):
        self.reactome_id = reactome_id
        self.wikidata_sparql = wd_sparql
        self.reference = reference
        self.species = species

        self.match_url = "http://identifiers.org/reactome:"+reactome_id

        self.missing_go_terms = []
        self.missing_citations = []
        self.missing_reactome_references = []

    def add_go_term(self, property_list, result):
        """
            Function to add the instance of property for a GO term
            This looks up the go identifier id in wikidata so that it can create the appropriate link
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        term_to_add = acquire_wikidata_links.WDGetData('goterm', 'P31', self.wikidata_sparql)
        term_to_add.add_term(result['goTerm']['value'], property_list, self.reference)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['goterms']:
                global_variables.used_wd_ids['goterms'].append(term)

    def add_citations(self, property_list, result):
        """
            Function to add the cites property
            This looks up the pudmed id in wikidata so that it can create the appropriate link

            This is copied from lines 170 - 188 of PathwayBot.py as of Mar 13

        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        pubmed_citations = []
        for citation in result['publication']['value']:
            pubmed_citations.append("\""+citation.replace("http://identifiers.org/pubmed/", "")+"\"")

        if not pubmed_citations:
            return

        term_to_add = acquire_wikidata_links.WDGetData('pmid', 'P2860', self.wikidata_sparql)
        term_to_add.add_multiple_terms(pubmed_citations, property_list, self.reference)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['pmid']:
                global_variables.used_wd_ids['pmid'].append(term)

    def add_part_of(self, property_list, result):
        """ Function to add the part of property
            This looks up the reactome id in wikidata so that it can create the appropriate lin
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        part_of = []
        for partof in result['isPartOf']['value']:
            part_of.append("\""+partof+"\"")

        if not part_of:
            return

        term_to_add = acquire_wikidata_links.WDGetData('reactomeid', 'P361', self.wikidata_sparql)
        term_to_add.add_multiple_terms(part_of, property_list, self.reference)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['reactome']:
                global_variables.used_wd_ids['reactome'].append(term)

    def add_haspart(self, property_list, result):
        """
            Function to add the has part property
            This looks up the reactome id in wikidata so that it can create the appropriate link
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        has_part = []
        for partof in result['hasPart']['value']:
            has_part.append("\""+partof+"\"")

        if not has_part:
            return

        term_to_add = acquire_wikidata_links.WDGetData('reactomeid', 'P527', self.wikidata_sparql)
        term_to_add.add_multiple_terms(has_part, property_list, self.reference)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['reactome']:
                global_variables.used_wd_ids['reactome'].append(term)


class AddPathway(AddEntry):
    """
    Class to add a Pathway entry
    """
    def __init__(self, reactome_id, wd_sparql, reference, species):
        AddEntry.__init__(self, reactome_id, wd_sparql, reference, species)

    def add_pathway(self, property_list, result):
        """
        function to add pathway item to wikidata
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        # add instance of biological pathway
        property_list["P31"] = [wdi_core.WDItemID(value="Q4915012", prop_nr="P31",
                                                  references=[copy.deepcopy(self.reference)])]

        # P2888 = exact match
        property_list["P2888"] = [wdi_core.WDUrl(self.match_url, prop_nr='P2888',
                                                 references=[copy.deepcopy(self.reference)])]

        # P703 = found in taxon
        property_list["P703"] = [wdi_core.WDItemID(value=self.species, prop_nr='P703',
                                                   references=[copy.deepcopy(self.reference)])]

        # P3937 = Reactome ID
        property_list["P3937"] = [wdi_core.WDString(value=self.reactome_id, prop_nr='P3937')]

        AddEntry.add_go_term(self, property_list, result)
        AddEntry.add_citations(self, property_list, result)
        AddEntry.add_haspart(self, property_list, result)
        AddEntry.add_part_of(self, property_list, result)


class AddEntity(AddEntry):
    """
    Class to add a entity entry
    """
    def __init__(self, reactome_id, wd_sparql, reference, species):
        AddEntry.__init__(self, reactome_id, wd_sparql, reference, species)
        self.complex_portal = 'https://www.ebi.ac.uk/complexportal/complex/'

    def create_complex_portal_reference(self, cp_id):
        ref_stated_in = wdi_core.WDItemID(value="Q47196990", prop_nr='P248', is_reference=True)
        str_time_now = strftime("+%Y-%m-%dT00:00:00Z", gmtime())
        ref_retrieved = wdi_core.WDTime(str_time_now, prop_nr='P813', is_reference=True)
        ref_url = wdi_core.WDString(self.complex_portal+cp_id, prop_nr='P854', is_reference=True)
        reference = [ref_stated_in, ref_retrieved, ref_url]
        return reference

    def add_entity(self, property_list, result):
        """
        function to add pathway item to wikidata
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        et = result['entitytype']
        if et == 'COMP':
            wditem_value = 'Q420927'
        elif et == 'DS':
            wditem_value = 'Q47461827'
        elif et == 'CS':
            wditem_value = 'Q47461807'
        elif et == 'OS':
            wditem_value = 'Q49980450'
        else:
            return

        # P31 = instance of
        cpref = []
        if result['cportal'] != '':
            cpref = self.create_complex_portal_reference(result['cportal'])
        if cpref:
            property_list["P31"] = [wdi_core.WDItemID(value=wditem_value, prop_nr="P31",
                                                      references=[copy.deepcopy(self.reference), cpref])]
        else:
            property_list["P31"] = [wdi_core.WDItemID(value=wditem_value, prop_nr="P31",
                                                      references=[copy.deepcopy(self.reference)])]

        # P2888 = exact match
        property_list["P2888"] = [wdi_core.WDUrl(self.match_url, prop_nr='P2888',
                                                 references=[copy.deepcopy(self.reference)])]

        # P703 = found in taxon
        property_list["P703"] = [wdi_core.WDItemID(value=self.species, prop_nr='P703',
                                                   references=[copy.deepcopy(self.reference)])]

        # P3937 = Reactome ID
        property_list["P3937"] = [wdi_core.WDString(value=self.reactome_id, prop_nr='P3937')]

        self.add_entity_parts(property_list, result)

    def add_entity_parts(self, property_list, result, part_type=''):
        """
            Function to write the parts of an entity which might be
            other reactome entities such as sets containing complexes
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        has_part = []
        part_qty = []
        has_protein = []
        protein_qty = []
        has_simple = []
        simple_qty = []
        partname = 'hasPart'
        if part_type != '':
            partname = part_type

        for partof in result[partname]['value']:
            if partof == 'null':
                break
            datatype, ref, quantity, st_id = partof.split(' ')
            if datatype == 'EWASMOD':
                # ignore these for now
                continue
            elif datatype == 'EWAS':
                protein = "\""+ref+"\""
                if protein not in has_protein:
                    has_protein.append(protein)
                    protein_qty.append(quantity)
            elif datatype == "SE":
                se = "\""+ref+"\""
                if se not in has_simple:
                    has_simple.append(se)
                    simple_qty.append(quantity)
            elif self.is_reactome_datatype(datatype):
                part = "\""+st_id+"\""
                if part not in has_part:
                    has_part.append(part)
                    part_qty.append(quantity)

        term_to_add = acquire_wikidata_links.WDGetData('reactomeid', 'P527', self.wikidata_sparql)
        term_to_add.add_multiple_terms(has_part, property_list, self.reference, part_qty, part_type)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['reactome']:
                global_variables.used_wd_ids['reactome'].append(term)

        term_to_add = acquire_wikidata_links.WDGetData('uniprotid', 'P527', self.wikidata_sparql)
        term_to_add.add_multiple_terms(has_protein, property_list, self.reference, protein_qty, part_type)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['proteins']:
                global_variables.used_wd_ids['proteins'].append(term)

        term_to_add = acquire_wikidata_links.WDGetData('chebi', 'P527', self.wikidata_sparql)
        term_to_add.add_multiple_terms(has_simple, property_list, self.reference, simple_qty, part_type)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['chebi']:
                global_variables.used_wd_ids['chebi'].append(term)

    def is_reactome_datatype(self, dt):
        if dt == 'COMP':
            return True
        elif dt == 'OS':
            return True
        elif dt == 'CS':
            return True
        elif dt == 'DS':
            return True
        else:
            return False

class AddReaction(AddEntity):
    """
    Class to add a Reaction entry
    """
    def __init__(self, reactome_id, wd_sparql, reference, species):
        AddEntry.__init__(self, reactome_id, wd_sparql, reference, species)

    def add_reaction(self, property_list, result):
        """
        function to add pathway item to wikidata
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        # add instance of biological process
        property_list["P31"] = [wdi_core.WDItemID(value="Q2996394", prop_nr="P31",
                                                  references=[copy.deepcopy(self.reference)])]

        # P2888 = exact match
        property_list["P2888"] = [wdi_core.WDUrl(self.match_url, prop_nr='P2888',
                                                 references=[copy.deepcopy(self.reference)])]

        # P703 = found in taxon
        property_list["P703"] = [wdi_core.WDItemID(value=self.species, prop_nr='P703',
                                                   references=[copy.deepcopy(self.reference)])]

        # P3937 = Reactome ID
        property_list["P3937"] = [wdi_core.WDString(value=self.reactome_id, prop_nr='P3937')]

        AddEntry.add_go_term(self, property_list, result)
        AddEntry.add_citations(self, property_list, result)
        AddEntry.add_part_of(self, property_list, result)
        AddEntity.add_entity_parts(self, property_list, result, 'inputs')
        AddEntity.add_entity_parts(self, property_list, result, 'outputs')
        AddEntity.add_entity_parts(self, property_list, result, 'mods')

class AddModProt(AddEntry):
    """
    Class to add a Pathway entry
    """
    def __init__(self, reactome_id, wd_sparql, reference, species):
        AddEntry.__init__(self, reactome_id, wd_sparql, reference, species)

    def add_modprot(self, property_list, result):
        """
        function to add modified protein item to wikidata
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """

        # P279 = subclass of
        term_to_add = acquire_wikidata_links.WDGetData('uniprotid', 'P279', self.wikidata_sparql)
        term_to_add.add_term(result['protein']['value'], property_list, self.reference)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['proteins']:
                global_variables.used_wd_ids['proteins'].append(term)

        # P703 = found in taxon
        property_list["P703"] = [wdi_core.WDItemID(value=self.species, prop_nr='P703',
                                                   references=[copy.deepcopy(self.reference)])]

        # P2888 = exact match
        url = 'http://purl.obolibrary.org/obo/{0}'.format(global_variables.get_pro_for_id(self.reactome_id))
        property_list["P2888"] = [wdi_core.WDUrl(url, prop_nr='P2888',
                                                 references=[copy.deepcopy(self.reference)])]

        # P3937 = Reactome ID
        property_list["P3937"] = [wdi_core.WDString(value=self.reactome_id, prop_nr='P3937')]

        AddModProt.add_modprot_parts(self, property_list, result)

    def add_modprot_parts(self, property_list, result):
        """
            Function to write the parts of a modified protein which might be
            other reactome entities such as sets containing complexes
        :param property_list: the list of property entries that will be made
        :param result: the data from Reactome
        :return:
        """
        has_part = []
        part_qty = []

        for partof in result['hasPart']['value']:
            name, modref_brackets, loc = partof.split(' ')
            modref = modref_brackets[1:len(modref_brackets)-1]
            chebi = global_variables.get_chebi_from_mod(modref)
            if chebi != '':
                has_part.append('\"' + chebi + '\"')
                part_qty.append(loc)

        term_to_add = acquire_wikidata_links.WDGetData('chebi', 'P527', self.wikidata_sparql)
        term_to_add.add_multiple_terms(has_part, property_list, self.reference, None, '', part_qty)
        for term in term_to_add.get_missing_terms():
            if term not in global_variables.used_wd_ids['chebi']:
                global_variables.used_wd_ids['chebi'].append(term)



