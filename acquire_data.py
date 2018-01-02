__author__ = 'Sarah Keating'

from wikidataintegrator import wdi_core


class WDGetData():
    """
    Class to populate a particular set of claims
    """
    def __init__(self, property_name, property_id, wd_query):
        self.property = property_name
        self.id = property_id
        self.wikidata_sparql = wd_query
        self.missing_terms = []

    def add_term(self, value, property_list):
        """
            Function to add the instance of teh property to the property_list
            This looks up the identifier id in wikidata so that it can create the appropriate link
        :param value:
        :param property_list:
        :return:
        """
        term = '\"' + value + '\"'
        if term == '""':
            return

        query = "SELECT * WHERE { VALUES ?goterm {"
        query += term
        query += "} ?item wdt:P686 ?goterm .}"
    #    print(query)

        found = False
        self.wikidata_sparql.setQuery(query)
        wikidata_results = self.wikidata_sparql.query().convert()

        for wikidata_result in wikidata_results["results"]["bindings"]:
            found = True
            # P31 = instance of
            if self.id not in property_list.keys():
                property_list[self.id] = []
            property_list[self.id].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""),
                                                            prop_nr=self.id,
                                                            references=None))
                                              # references=[copy.deepcopy(reference)]))
        if not found:
            self.missing_terms.append(term)
