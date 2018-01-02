__author__ = 'Sarah'

import acquire_data


class AddEntry:
    """
    class to create the set of data for a base wikidata entry
    """
    def __init__(self, wd_sparql, reference):
        self.wikidata_sparql = wd_sparql
        self.reference = reference
        self.missing_go_terms = []
        self.missing_citations = []
        self.missing_reactome_references = []

    def add_go_term(self, prep, result):
        """
            Function to add the instance of property for a GO term
            This looks up the go identifier id in wikidata so that it can create the appropriate link
        :param prep:
        :param result:
        :return:
        """
        addgo = acquire_data.WDGetData('goterm', 'P31', self.wikidata_sparql)
        addgo.add_term(result['goTerm']['value'], prep, self.reference)
        for term in addgo.get_missing_terms():
            self.missing_go_terms.append(term)

    def add_citations(self, prep, result):
        """
            Function to add the cites property
            This looks up the pudmed id in wikidata so that it can create the appropriate link

            This is copied from lines 170 - 188 of PathwayBot.py as of Mar 13

        :param prep:
        :param result:
        :return:
        """
        pubmed_citations = []
        for citation in result['publication']['value']:
            pubmed_citations.append("\""+citation.replace("http://identifiers.org/pubmed/", "")+"\"")

        if not pubmed_citations:
            return

        addgo = acquire_data.WDGetData('pmid', 'P2860', self.wikidata_sparql)
        addgo.add_multiple_terms(pubmed_citations, prep, self.reference)
        for term in addgo.get_missing_terms():
            self.missing_citations.append(term)

    def add_part_of(self, prep, result):
        """ Function to add the part of property
            This looks up the reactome id in wikidata so that it can create the appropriate lin
        :param prep:
        :param result:
        :return:
        """
        part_of = []
        for partof in result['isPartOf']['value']:
            part_of.append("\""+partof+"\"")

        if not part_of:
            return

        addgo = acquire_data.WDGetData('reactomeid', 'P527', self.wikidata_sparql)
        addgo.add_multiple_terms(part_of, prep, self.reference)
        for term in addgo.get_missing_terms():
            self.missing_reactome_references.append(term)

    def add_haspart(self, prep, result):
        """
            Function to add the has part property
            This looks up the reactome id in wikidata so that it can create the appropriate link
        :param prep:
        :param result:
        :return:
        """
        has_part = []
        for partof in result['hasPart']['value']:
            has_part.append("\""+partof+"\"")

        if not has_part:
            return

        addgo = acquire_data.WDGetData('reactomeid', 'P361', self.wikidata_sparql)
        addgo.add_multiple_terms(has_part, prep, self.reference)
        for term in addgo.get_missing_terms():
            self.missing_reactome_references.append(term)

class AddPathway(AddEntry):

    def __init__(self, wd_sparql, reference):
        AddEntry.__init__(self, wd_sparql, reference)

    def add_pathway(self, prep, result):
        AddEntry.add_go_term(self, prep, result)
        AddEntry.add_citations(self, prep, result)
        AddEntry.add_haspart(self, prep, result)
        AddEntry.add_part_of(self, prep, result)

