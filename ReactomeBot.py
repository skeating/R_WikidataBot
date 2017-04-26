__author__ = 'Sarah'

from wikidataintegrator import wdi_core, wdi_login
import DisplayItem
import os
import sys
import pprint
from time import gmtime, strftime
import copy



# test getting data
#server='test.wikidata.org'
server='www.wikidata.org'


def create_reference(result):
    """
    create the reference that is added to many properties
    tailored for Reactome
    """
    refStatedIn = wdi_core.WDItemID(value="Q2134522", prop_nr='P248', is_reference=True)
    timeStringNow = strftime("+%Y-%m-%dT00:00:00Z", gmtime())
    refRetrieved = wdi_core.WDTime(timeStringNow, prop_nr='P813', is_reference=True)
    # will need to add the Reactome ID reference which will be specific to the item
    refReactome = None
#    refReactome = wdi_core.WDString(result['pwId']['value'], prop_nr='PXXXX', is_reference=True)
    if refReactome is None:
        reference = [refStatedIn, refRetrieved]
    else:
        reference = [refStatedIn, refRetrieved, refReactome]
    return reference



def show_item(id, domain=None, wdpage=None):
    if not wdpage:
        print('Item found by id: {0} domain {1}'.format(id, domain))
        wdpage = wdi_core.WDItemEngine(wd_item_id=id, server=server, domain=domain)
    d = DisplayItem.DisplayItem(wdpage.get_wd_json_representation(), server)
    d.show_item()

def create_or_update_items(logincreds, results):
    """ this function takes the results dictionary from Reactome;
    which hopefully emulates the JSON returned by the wikipathways query;
    and adds or updates each item

    Code here is exactly taken from PathwayBot.py as of Mar 13 lines 142 - end

    EXCEPT:

    wikipathways_reference has been replaced with a new version specific for Reactome

    Reactome results include a 'pwDescription'

    No Wikipathways Id added :-)

    Exact match property amended to Reactome reference

    No URL added

    the section adding the citations has been changed to no longer query wikipathways

    """

    prep = dict()
    for result in results["results"]["bindings"]:
        reference = create_reference(result)
        match_url = "http://identifiers.org/reactome/REACTOME:"+result["pwId"]["value"]
        print('Creating/updating pathway: ' + result["pwId"]["value"])

        # P31 = instance of pathway
        prep["P31"] = [wdi_core.WDItemID(value="Q28864279",prop_nr="P31", references=[copy.deepcopy(reference)])]

        # P2888 = exact match
        prep["P2888"] = [wdi_core.WDUrl(match_url, prop_nr='P2888', references=[copy.deepcopy(reference)])]

        # P703 = found in taxon, Q15978631 = "Homo sapiens"
        prep["P703"] = [wdi_core.WDItemID(value="Q15978631", prop_nr='P703', references=[copy.deepcopy(reference)])]


        ## commented out the pmid queries for now
        # query = """
        # PREFIX wp:    <http://vocabularies.wikipathways.org/wp#>
        # PREFIX dcterms: <http://purl.org/dc/terms/>
        # select *
        #
        # WHERE {
        # ?pubmed  a       wp:PublicationReference ;
        #         dcterms:isPartOf <"""
        #
        # query+= result["pathway"]["value"]
        # query += """> .}
        #
        # """
        # wikipathways_sparql.setQuery(query)
        # pubmed_results = wikipathways_sparql.query().convert()
        # pubmed_citations = []
        # for pubmed_result in pubmed_results["results"]["bindings"]:
        #     pubmed_citations.append("\""+pubmed_result["pubmed"]["value"].replace("http://identifiers.org/pubmed/", "")+"\"")
        #
        # query = "SELECT * WHERE { VALUES ?pmid {"
        # query += " ".join(pubmed_citations)
        # query += "} ?item wdt:P698 ?pmid .}"
        # # print(query)
        # wikidata_sparql.setQuery(query)
        # wikidata_results = wikidata_sparql.query().convert()
        # for wikidata_result in wikidata_results["results"]["bindings"]:
        #     # P2860 = cites
        #     if 'P2860' not in prep.keys():
        #         prep["P2860"] = []
        #     prep['P2860'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P2860',
        #                                        references=[copy.deepcopy(wikipathways_reference)]))

 #       pprint.pprint(prep)
        data2add = []
        for key in prep.keys():
            for statement in prep[key]:
                data2add.append(statement)
 #               print(statement.prop_nr, statement.value)
        # wdPage = wdi_core.WDItemEngine( item_name=result["pwLabel"]["value"], data=data2add, server="www.wikidata.org", domain="genes", fast_run=fast_run, fast_run_base_filter=fast_run_base_filter)
        wdPage = wdi_core.WDItemEngine(item_name=result["pwLabel"]["value"], data=data2add, server="www.wikidata.org",
                                       domain="pathway")

        wdPage.set_label(result["pwLabel"]["value"])
        wdPage.set_description (result['pwDescription']['value'])

#        wd_json_representation = wdPage.get_wd_json_representation()
#        pprint.pprint(wd_json_representation)

        return_value = 0
        if (server == 'test.wikidata.org'):
           return_value = wdPage.write(logincreds)

        if return_value != 0:
            show_item(return_value)
        else:
            show_item(return_value, wdpage=wdPage)


def get_data_from_reactome():
    f = open('reactome_data.csv', 'r')
    lines = f.readlines()
    f.close()
    pathways = []
    for line in lines:
        id,label,description = line.split(',')
        pathway = dict({'pwId': {'value': id, 'type': 'string'},
                        'pwLabel': {'value': label, 'type': 'string'},
                        'pwDescription': {'value': description, 'type': 'string'}})
        pathways.append(pathway)
    p = [
        {"pwId": { "value": 'R-HSA-val1', 'type': 'string'},
          "pwLabel": { "value": 'label 1', 'type': 'string'},
 #         'pathway': { "value": 'pathway1', 'type': 'string'},
          'pwDescription': { "value": 'This is pathway1', 'type': 'string'}
        },
        {"pwId": { "value": 'R-HSA-val2', 'type': 'string'},
          "pwLabel": { "value": 'label 2', 'type': 'string'},
 #         'pathway': { "value": 'pathway2', 'type': 'string'},
          'pwDescription': { "value": 'This is pathway2', 'type': 'string'}
        }
    ]
    b = dict({'bindings': pathways})
    results = dict({'results': b})
    return results


def main(args):
    logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
    results = get_data_from_reactome();
    create_or_update_items(logincreds, results)


# #   id = create_item(logincreds)
#     id = add_statement(logincreds)
#     print (id)
# #     name = 'Citric acid cycle (TCA cycle)'
# #     id = 'Q28031545'
# #     domain='pathway'
# # #    print (id)
# #
#     id = 'Q58879'
#     show_item(id)
# #     print('\n')
# #     show_item_by_name(name)
# #     print('\n')
# #     show_item(id, domain)
# #     print('\n')
# #     show_item_by_name(name, domain)

if __name__ == '__main__':
    main(sys.argv)

## just to keep it around
#adds teh statements to existing item Q59496
# note it overwrites any existing statements with same property
def add_statement(logincreds, prep):
    prep["31"] = [wdi_core.WDUrl(value='https://www.another.xyz', prop_nr='P31')]
    prep["29943"] = [wdi_core.WDItemID(value='Q59494', prop_nr='P29943')]
    data2add = []
    for key in prep.keys():
        for statement in prep[key]:
            data2add.append(statement)
            print(statement.prop_nr, statement.value)
    wdPage = wdi_core.WDItemEngine(wd_item_id='Q59496', server=server)
    wdPage.update(data2add)
    return wdPage.write(login=logincreds, edit_summary='adding label/description')



