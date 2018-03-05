__author__ = 'Sarah Keating'

from wikidataintegrator import wdi_core
import copy
import global_variables


class WDGetData():
    """
    Class to populate a particular set of claims based on the property that
    identifies these terms in Wikidata

    Supported terms - see global variables
    """
    def __init__(self, property_name, property_id, wd_query):
        self.property = property_name
        self.property_id = property_id
        self.wikidata_sparql = wd_query

        self.missing_terms = []

        self.open_brace = '{'
        self.close_brace = '}'
        self.property_reference = self.get_property_number()

    ####################################################################
    #
    # Functions to add terms to the list of statements for this property

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

    def add_multiple_terms(self, value, property_list, reference, quantity=None, part_type='', loc=None):
        """
            Function to add the instance of the property to the property_list
            This looks up the identifier id in wikidata so that it can create the appropriate link

        :param value: list of values of the term
        :param property_list: list of properties that will be added to the entry
        :param quantity: list of the quantity of substance in the given complex/set/reaction
        :param part_type: string representing the role of a substance in a reaction
        :param loc: list of ordinals for phosphorylation sites
        """
        if self.property_reference == '' or len(value) == 0:
            return
        terms = value

        query = "SELECT * WHERE {0} VALUES ?{1} {0}".format(self.open_brace, self.property)
        query += " ".join(terms)
        query += "{0} ?item wdt:{2} ?{1} .{0}".format(self.close_brace, self.property, self.property_reference)
        self.wikidata_sparql.setQuery(query)
        wikidata_results = self.wikidata_sparql.query().convert()

        for wikidata_result in wikidata_results["results"]["bindings"]:
            wikidata_entity = wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", "")
            total_qualifier = self.create_qualifier(wikidata_result, value, quantity, part_type, loc)
            if self.property_id not in property_list.keys():
                property_list[self.property_id] = []
            property_list[self.property_id].append(wdi_core.WDItemID(value=wikidata_entity,
                                                                     prop_nr=self.property_id,
                                                                     references=[copy.deepcopy(reference)],
                                                                     qualifiers=total_qualifier))
            result = "\"{0}\"".format(wikidata_result[self.property]['value'])
            if result in terms:
                terms.remove(result)

        for term in terms:
            self.missing_terms.append(term)

    #############################################################################
    # Functions to create qualifiers

    def create_qty_qualifier(self, wdresult, value, quantity):
        """
            Function to create the quantity qualifier to respresent stoichiometry

        :param wdresult: results from a wikidata query for a list of items
        :param value: list of the items
        :param quantity: list of the quantity for each item (indexed as in value)
        :return: a wikidata qualifier statement for quantity
        """
        this_item = '\"' + wdresult[self.property]['value'] + '\"'
        if this_item in value:
            this_index = value.index(this_item)
            if this_index < len(quantity):
                qualifier = wdi_core.WDQuantity(int(quantity[this_index]), prop_nr='P1114', is_qualifier=True)
                return qualifier
        return []

    @staticmethod
    def create_part_qualifier(part_type):
        """
            Function to create qualifier to indicate the role of a substance in a reaction
        :param part_type: string either 'inputs', 'outputs' or 'mods'
        :return: wikidata qualifier indication instanceOf and
                 the wd item for the relevant reactant/product/modifier term
        """
        qualifier = []
        if part_type == 'inputs':
            qualifier = wdi_core.WDItemID('Q45342565', prop_nr='P31', is_qualifier=True)
        elif part_type == 'outputs':
            qualifier = wdi_core.WDItemID('Q45342745', prop_nr='P31', is_qualifier=True)
        elif part_type == 'mods':
            qualifier = wdi_core.WDItemID('Q45342890', prop_nr='P31', is_qualifier=True)
        return qualifier

    def create_series_qualifier(self, wdresult, value, quantity):
        """
            Function to create the quantity qualifier to respresent series ordinal of phosphorylation

        :param wdresult: results from a wikidata query for a list of items
        :param value: list of the items
        :param quantity: list of the ordinal for each item (indexed as in value)
        :return: a wikidata qualifier statement for series ordinal
        """
        this_item = '\"' + wdresult[self.property]['value'] + '\"'
        if this_item in value:
            this_index = value.index(this_item)
            if this_index < len(quantity):
                qualifier = wdi_core.WDQuantity(int(quantity[this_index]), prop_nr='P1545', is_qualifier=True)
                return qualifier
        return []

    def create_qualifier(self, wdresult, value, quantity, part_type, location):
        """
            Function to create a qualifier if it is appropriate

        :param wdresult: results from a wikidata query for a list of items
        :param value: list of the items
        :param quantity: list of the quantity for each item (indexed as in value)
        :param part_type: string either 'inputs', 'outputs' or 'mods'
        :param location: list of locations for modified residues

            Note this function calls create_qty_qualifier and create_part_qualifier
            and constructs the overall qualifier if appropriate

        :return: qualifier, if appropriate, None otherwise
        """
        quantity_qualifier = None
        part_qualifier = None
        series_qualifier = None
        total_qualifier = []
        if quantity:
            quantity_qualifier = self.create_qty_qualifier(wdresult, value, quantity)
        if part_type != '':
            part_qualifier = self.create_part_qualifier(part_type)
        if location:
            series_qualifier = self.create_series_qualifier(wdresult, value, location)
        if quantity_qualifier:
            if part_qualifier:
                total_qualifier = [quantity_qualifier, part_qualifier]
            else:
                total_qualifier = [quantity_qualifier]
        elif part_qualifier:
            total_qualifier = [part_qualifier]
        elif series_qualifier:
            total_qualifier = [series_qualifier]
        return total_qualifier

    # helper functions

    def get_property_number(self):
        """
          Function to get the relevant wd entry number for the property being added
          Note these are terms that we expect to find already in wikidata - such as pmid
          and we need the property number to create appropriate queries
        :return: the wikidata property id number eg P3937 for Reactome ID
        """
        number = ''
        for prop in global_variables.supported_properties:
            if prop['name'] == self.property:
                number = prop['id']
                break
        return number

    def get_missing_terms(self):
        """
            Function to retrieve any terms that were missing in wikidata
            These are logged when a query fails to find a particular term e.g. pmid
        :return: list of missing terms for the property being used
        """
        return self.missing_terms
