__author__ = 'Sarah Keating'

from wikidataintegrator import wdi_core
import copy

class WDGetData():
    """
    Class to populate a particular set of claims
    """
    def __init__(self, property_name, property_id, wd_query):
        self.property = property_name
        self.property_id = property_id
        self.wikidata_sparql = wd_query

        self.missing_terms = []

        self.supported_properties = [{'id': 'P686', 'name': 'goterm'},
                                     {'id': 'P3937', 'name': 'reactomeid'},
                                     {'id': 'P698', 'name': 'pmid'},
                                     {'id': 'P352', 'name': 'uniprotid'},
#                                     {'id': 'P527', 'name': 'reactomeid'}
                                     ]
        self.open_brace = '{'
        self.close_brace = '}'
        self.property_reference = self.get_property_number()

    def add_term(self, value, property_list, reference):
        """
            Function to add the instance of the property to the property_list
            This looks up the identifier id in wikidata so that it can create the appropriate link
        :param value: value of the term
        :param property_list: list of properties that will be added to the entry
        :return: None
        """
        if self.property_reference == '':
            return

        term = '\"' + value + '\"'
        if term == '""':
            return

        query = "SELECT * WHERE {0} VALUES ?{1} {0}".format(self.open_brace, self.property)
        query += term
        query += "{0} ?item wdt:{2} ?{1} .{0}".format(self.close_brace, self.property, self.property_reference)
    #    print(query)

        found = False
        self.wikidata_sparql.setQuery(query)
        wikidata_results = self.wikidata_sparql.query().convert()

        for wikidata_result in wikidata_results["results"]["bindings"]:
            found = True
            wikidata_entity = wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", "")
            if self.property_id not in property_list.keys():
                property_list[self.property_id] = []
            property_list[self.property_id].append(wdi_core.WDItemID(value=wikidata_entity,
                                                                     prop_nr=self.property_id,
                                                                     references=[copy.deepcopy(reference)]))
        if not found:
            self.missing_terms.append(term)

    def add_multiple_terms(self, value, property_list, reference):
        """
            Function to add the instance of the property to the property_list
            This looks up the identifier id in wikidata so that it can create the appropriate link
        :param value: list of values of the term
        :param property_list: list of properties that will be added to the entry
        :return: None
        """
        if self.property_reference == '':
            return
        terms = value

        query = "SELECT * WHERE {0} VALUES ?{1} {0}".format(self.open_brace, self.property)
        query += " ".join(terms)
        query += "{0} ?item wdt:{2} ?{1} .{0}".format(self.close_brace, self.property, self.property_reference)
        self.wikidata_sparql.setQuery(query)
        wikidata_results = self.wikidata_sparql.query().convert()

        for wikidata_result in wikidata_results["results"]["bindings"]:
            wikidata_entity = wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", "")
            if self.property_id not in property_list.keys():
                property_list[self.property_id] = []
            property_list[self.property_id].append(wdi_core.WDItemID(value=wikidata_entity,
                                                                     prop_nr=self.property_id,
                                                                     references=[copy.deepcopy(reference)]))
            result = "\"{0}\"".format(wikidata_result[self.property]['value'])
            if result in terms:
                terms.remove(result)

        for term in terms:
            self.missing_terms.append(term)

    def get_property_number(self):
        number = ''
        for prop in self.supported_properties:
            if prop['name'] == self.property:
                number = prop['id']
                break
        return number

    def get_missing_terms(self):
        return self.missing_terms