__author__ = 'Sarah'

from wikidataintegrator import wdi_core, wdi_login
import DisplayItem
import os
import sys
import pprint
from time import gmtime, strftime
import copy
from SPARQLWrapper import SPARQLWrapper, JSON



# test getting data
#server='test.wikidata.org'
server='www.wikidata.org'

supported_species = [dict({'ReactomeCode': 'HSA', 'name': 'Homo sapiens', 'WDItem': 'Q15978631'})]
current_species = 0 # index of species

# Stating SPARQL endpoints
wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
wikidata_sparql.setReturnFormat(JSON)


def show_item(id, domain=None, wdpage=None):
    '''
        My helper function to display the item information
        This merely parses the json output but I found it easier
    '''
    if not wdpage:
        print('Item found by id: {0} domain {1}'.format(id, domain))
        wdpage = wdi_core.WDItemEngine(wd_item_id=id, server=server, domain=domain)
    d = DisplayItem.DisplayItem(wdpage.get_wd_json_representation(), server)
    d.show_item()


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



def add_go_term(prep, result, reference):
    ''' Function to add the instance of property for a GO term
        This looks up the go identifier id in wikidata so that it can create the appropriate link
    '''
    goterm = '\"' + result['goTerm']['value'] + '\"'
    if goterm == '""':
        return

    query = "SELECT * WHERE { VALUES ?goterm {"
    query += goterm
    query += "} ?item wdt:P686 ?goterm .}"
#    print(query)

    wikidata_sparql.setQuery(query)
    wikidata_results = wikidata_sparql.query().convert()

    for wikidata_result in wikidata_results["results"]["bindings"]:
        # P31 = instance of
        if 'P31' not in prep.keys():
            prep["P31"] = []
        prep['P31'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P31',
                                           references=[copy.deepcopy(reference)]))


def add_citations(prep, result, reference):
    ''' Function to add the cites property
        This looks up the pudmed id in wikidata so that it can create the appropriate link

        This is copied from lines 170 - 188 of PathwayBot.py as of Mar 13

        EXCEPT

        the query to wikipathways is removed; the appropriate PubMed Id link is supplied
        by the reactome export
    '''
    pubmed_citations = []
    for citation in result['publication']['value']:
        pubmed_citations.append("\""+citation.replace("http://identifiers.org/pubmed/", "")+"\"")

    query = "SELECT * WHERE { VALUES ?pmid {"
    query += " ".join(pubmed_citations)
    query += "} ?item wdt:P698 ?pmid .}"
#    print(query)

    wikidata_sparql.setQuery(query)
    wikidata_results = wikidata_sparql.query().convert()

    for wikidata_result in wikidata_results["results"]["bindings"]:
        # P2860 = cites
        if 'P2860' not in prep.keys():
            prep["P2860"] = []
        prep['P2860'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P2860',
                                           references=[copy.deepcopy(reference)]))


def create_or_update_items(logincreds, results, test=0):
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

    the section adding the citations has been changed to use a separate function add_citations

    """
    if results is None:
        return
    prep = dict()
    for result in results["results"]["bindings"]:
        if result['pwLabel']['value'] == '':
            continue
        create_or_update_item(logincreds, result, test, prep)

def create_or_update_item(logincreds, result, test, prep):
    if result['pwLabel']['value'] == '':
            return False
    reference = create_reference(result)
    match_url = "http://identifiers.org/reactome/REACTOME:"+result["pwId"]["value"]
    print('Creating/updating pathway: ' + result["pwId"]["value"])

    # P31 = instance of pathway
    prep["P31"] = [wdi_core.WDItemID(value="Q28864279",prop_nr="P31", references=[copy.deepcopy(reference)])]

    # P2888 = exact match
    prep["P2888"] = [wdi_core.WDUrl(match_url, prop_nr='P2888', references=[copy.deepcopy(reference)])]

    # P703 = found in taxon
    prep["P703"] = [wdi_core.WDItemID(value=supported_species[current_species]['WDItem'], prop_nr='P703', references=[copy.deepcopy(reference)])]

    # pmid queries happen here
    add_citations(prep, result, reference)
    add_go_term(prep, result, reference)
    data2add = []
    for key in prep.keys():
        for statement in prep[key]:
            data2add.append(statement)
#               print(statement.prop_nr, statement.value)
    # wdPage = wdi_core.WDItemEngine( item_name=result["pwLabel"]["value"], data=data2add, server="www.wikidata.org", domain="genes", fast_run=fast_run, fast_run_base_filter=fast_run_base_filter)
    wdPage = wdi_core.WDItemEngine(item_name=result["pwLabel"]["value"], data=data2add, server=server,
                                   domain="pathway")

    wdPage.set_label(result["pwLabel"]["value"])
    wdPage.set_description (result['pwDescription']['value'])

#        wd_json_representation = wdPage.get_wd_json_representation()
#        pprint.pprint(wd_json_representation)

    item_id_value = 0
    if (server == 'test.wikidata.org'):
       item_id_value = wdPage.write(logincreds)

    if item_id_value != 0:
        show_item(item_id_value)
    else:
        if (test):
            outfile = open('output_test.json', 'w')
            wd_json_representation = wdPage.get_wd_json_representation()
            pprint.pprint(wd_json_representation, outfile)
        else:
            show_item(item_id_value, wdpage=wdPage)
    return True



def parse_literature_references(reference):
    '''
    Takes the reference element and creates a list of the references
    '''
    lorefs = []
    length = len(reference)
    if reference.startswith('[') and reference.endswith(']'):
        modified_ref = reference[1:length-1]
    return modified_ref.split(';')



def get_data_from_reactome(filename='reactome_data.csv'):
    '''
    This function creates a JSON representation of the Reactome data from a precise csv export
    this emulates the results of the wikipathways query so common code can be used

    If a filename is not given it will look for the default file

    The form of the form of the csv file is:

    species,stableId,name,description,[publication;publication;...],None

    '''
    if not os.path.isfile(filename):
        print('{0} not found aborting ...'.format(filename))
        return None;

    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    pathways = []
    for line in lines:
        species,id,label,description,reference,goterm,endelement = line.split(',')
        # only deal with human at present
        if species != supported_species[current_species]['ReactomeCode']:
            continue
        lorefs = parse_literature_references(reference)
        pathway = dict({'pwId': {'value': id, 'type': 'string'},
                        'pwLabel': {'value': label, 'type': 'string'},
                        'pwDescription': {'value': description, 'type': 'string'},
                        'publication': {'value': lorefs, 'type': 'list'},
                        'goTerm': {'value': goterm, 'type': 'string'}})
        pathways.append(pathway)
    b = dict({'bindings': pathways})
    results = dict({'results': b})
    return results


def main(args):
    logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
    results = get_data_from_reactome('test/test_reactome_data.csv');
    create_or_update_items(logincreds, results)

if __name__ == '__main__':
    main(sys.argv)

