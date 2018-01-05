__author__ = 'Sarah'

import acquire_wikidata_links
import global_variables
from wikidataintegrator import wdi_core
import copy


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
        addgo = acquire_wikidata_links.WDGetData('goterm', 'P31', self.wikidata_sparql)
        addgo.add_term(result['goTerm']['value'], property_list, self.reference)
        for term in addgo.get_missing_terms():
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

        addgo = acquire_wikidata_links.WDGetData('pmid', 'P2860', self.wikidata_sparql)
        addgo.add_multiple_terms(pubmed_citations, property_list, self.reference)
        for term in addgo.get_missing_terms():
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

        addgo = acquire_wikidata_links.WDGetData('reactomeid', 'P527', self.wikidata_sparql)
        addgo.add_multiple_terms(part_of, property_list, self.reference)
        for term in addgo.get_missing_terms():
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

        addgo = acquire_wikidata_links.WDGetData('reactomeid', 'P361', self.wikidata_sparql)
        addgo.add_multiple_terms(has_part, property_list, self.reference)
        for term in addgo.get_missing_terms():
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
