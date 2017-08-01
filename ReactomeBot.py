__author__ = 'Sarah'

from wikidataintegrator import wdi_core, wdi_login, wdi_property_store
import DisplayItem
import os
import sys
import pprint
from time import gmtime, strftime
import copy
from SPARQLWrapper import SPARQLWrapper, JSON

# global variables that need to be set/changed
# are we actually writing to wikidata
writing_to_WD = False
# do we use a date to show when retrieved or the Reactome version number
use_date_ref = True
version_no = 61

# test getting data
#server='test.wikidata.org'
server='www.wikidata.org'


supported_species = [dict({'ReactomeCode': 'HSA', 'name': 'Homo sapiens', 'WDItem': 'Q15978631'})]
current_species = 0  # index of species

# Stating SPARQL endpoints
wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
wikidata_sparql.setReturnFormat(JSON)

fast_run = True
fast_run_base_filter = dict({'P3937': '', 'P703': 'Q15978631'})

# tell the properties about reactome ID
wdi_property_store.wd_properties['P3937'] = {
        'datatype': 'string',
        'name': 'Reactome Pathway ID',
        'domain': ['pathways'],
        'core_id': 'True'
    }

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
    if use_date_ref:
        refRetrieved = wdi_core.WDTime(timeStringNow, prop_nr='P813', is_reference=True)
    else:
        refRetrieved = wdi_core.WDString('Version {0}'.format(version_no), prop_nr='P813', is_reference=True)
    refReactome = wdi_core.WDString(result['pwId']['value'], prop_nr='P3937', is_reference=True)
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

    if pubmed_citations == []:
        return

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


def add_part_of(prep, result, reference):
    ''' Function to add the part of property
        This looks up the reactome id in wikidata so that it can create the appropriate link
    '''
    part_of = []
    for partof in result['isPartOf']['value']:
        part_of.append("\""+partof+"\"")

    if part_of == []:
        return

    query = "SELECT * WHERE { VALUES ?reactomeid {"
    query += " ".join(part_of)
    query += "} ?item wdt:P3937 ?reactomeid .}"
#    print(query)

    wikidata_sparql.setQuery(query)
    wikidata_results = wikidata_sparql.query().convert()

    for wikidata_result in wikidata_results["results"]["bindings"]:
        # P361 = part of
        if 'P361' not in prep.keys():
            prep["P361"] = []
        prep['P361'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P361',
                                           references=[copy.deepcopy(reference)]))


def add_haspart(prep, result, reference):
    ''' Function to add the has part property
        This looks up the reactome id in wikidata so that it can create the appropriate link
    '''
    has_part = []
    for partof in result['hasPart']['value']:
        has_part.append("\""+partof+"\"")

    if has_part == []:
        return

    query = "SELECT * WHERE { VALUES ?reactomeid {"
    query += " ".join(has_part)
    query += "} ?item wdt:P3937 ?reactomeid .}"
#    print(query)

    wikidata_sparql.setQuery(query)
    wikidata_results = wikidata_sparql.query().convert()

    for wikidata_result in wikidata_results["results"]["bindings"]:
        # P527 = has part
        if 'P527' not in prep.keys():
            prep["P527"] = []
        prep['P527'].append(wdi_core.WDItemID(value=wikidata_result["item"]["value"].replace("http://www.wikidata.org/entity/", ""), prop_nr='P527',
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
    for result in results["results"]["bindings"]:
        prep = dict()
        if result['pwLabel']['value'] == '':
            continue
        create_or_update_item(logincreds, result, test, prep)

def create_or_update_item(logincreds, result, test, prep):
    if test:
        global writing_to_WD
        writing_to_WD = False
        global use_date_ref
        use_date_ref= False
        global version_no
        version_no = 59
    if result['pwLabel']['value'] == '':
            return False
    reference = create_reference(result)
    match_url = "http://identifiers.org/reactome:"+result["pwId"]["value"]
    print('Creating/updating pathway: ' + result["pwId"]["value"])

    # P31 = instance of pathway
    prep["P31"] = [wdi_core.WDItemID(value="Q4915012",prop_nr="P31", references=[copy.deepcopy(reference)])]

    # P2888 = exact match
    prep["P2888"] = [wdi_core.WDUrl(match_url, prop_nr='P2888', references=[copy.deepcopy(reference)])]

    # P703 = found in taxon
    prep["P703"] = [wdi_core.WDItemID(value=supported_species[current_species]['WDItem'], prop_nr='P703', references=[copy.deepcopy(reference)])]

    # P3937 = Reactome ID
    prep["P3937"] = [wdi_core.WDString(value=result["pwId"]["value"], prop_nr='P3937')]

    # pmid queries happen here
    add_citations(prep, result, reference)
    add_part_of(prep, result, reference)
    add_haspart(prep, result, reference)
    add_go_term(prep, result, reference)
    data2add = []
    for key in prep.keys():
        for statement in prep[key]:
            data2add.append(statement)
#               print(statement.prop_nr, statement.value)
#    wdPage = wdi_core.WDItemEngine( item_name=result["pwLabel"]["value"], data=data2add, server="www.wikidata.org",
#                                    domain="pathway", fast_run=fast_run, fast_run_base_filter=fast_run_base_filter)
    wdPage = wdi_core.WDItemEngine(item_name=result["pwLabel"]["value"], data=data2add, server=server,
                                   domain="pathway")

    wdPage.set_label(result["pwLabel"]["value"])
    wdPage.set_description(result['pwDescription']['value'])

    # wd_json_representation = wdPage.get_wd_json_representation()
    # pprint.pprint(wd_json_representation)

    if (writing_to_WD):
        item_id_value = wdPage.write(logincreds)

        if item_id_value != 0:
            print('https://www.wikidata.org/wiki/{0}'.format(item_id_value))
#            show_item(item_id_value)
    else:
        item_id_value = 0
        if (server == 'test.wikidata.org'):
           item_id_value = wdPage.write(logincreds)

        if item_id_value != 0:
            print(item_id_value)
            show_item(item_id_value)
        else:
            if (test):
                outfile = open('output_test.json', 'w')
                wd_json_representation = wdPage.get_wd_json_representation()
                pprint.pprint(wd_json_representation, outfile)
                return True
            else:
                show_item(item_id_value, wdpage=wdPage)
                print('\n')



def parse_list_references(reference):
    '''
    Takes the reference element and creates a list of the references
    '''
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

    species,stableId,name,description,[publication;publication;...],goterm,[part1;part2],[partof1;partof2],None

    '''
    if not os.path.isfile(filename):
        print('{0} not found aborting ...'.format(filename))
        return None;

    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    pathways = []
    for line in lines:
        variables = line.split(',')
        if len(variables) != 9:
            print('A line in the input csv file expects 9 comma separated entries')
            print('species,id,label,description,reference,goterm,haspart,ispartof,endelement')
            print('Re run WikidataExport to create an accurate file')
            return None
        else:
            species,id,label,description,reference,goterm,haspart,ispartof,endelement = line.split(',')
            # only deal with human at present
            if species != supported_species[current_species]['ReactomeCode']:
                continue
            lorefs = parse_list_references(reference)
            lo_haspart = parse_list_references(haspart)
            lo_ispartof = parse_list_references(ispartof)
            pathway = dict({'pwId': {'value': id, 'type': 'string'},
                            'pwLabel': {'value': label, 'type': 'string'},
                            'pwDescription': {'value': description, 'type': 'string'},
                            'publication': {'value': lorefs, 'type': 'list'},
                            'goTerm': {'value': goterm, 'type': 'string'},
                            'hasPart': {'value': lo_haspart, 'type': 'list'},
                            'isPartOf': {'value': lo_ispartof, 'type': 'list'}})
            pathways.append(pathway)
    b = dict({'bindings': pathways})
    results = dict({'results': b})
    return results


def check_settings(uname):
    print('Current settings are:')
    print('Writing to wikidata: {0}'.format('True' if writing_to_WD else 'False'))
    print('Reactome version: {0}'.format(version_no))
    print('Use date retrieved: {0}'.format('True' if use_date_ref else 'False'))
    if uname == 'SarahKeating':
        print('Using skeating account')
    else:
        print('Using bot account')
    var = input('Proceed (Y):')
    if var == 'Y':
        return True
    else:
        return False




def main(args):
    """Usage: ReactomeBot  WDusername, WDpassword (input-filename)
       This program take the input-filename or use test/test_reactome_data.csv
       if none given and write the wikidata pages
       NOTE: At present if will only actually write pages to test,
       the global variable writing_to_WD needs to set true
    """
    filename = 'test/test_reactome_data.csv'
    if len(args) < 3 or len(args) > 4:
        print(main.__doc__)
        sys.exit()
    elif len(args) == 4:
        filename = args[3]

    if check_settings(args[1]):
        try:
            logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
 #           logincreds = wdi_login.WDLogin(user=args[1], server=server)

        except Exception as e:
            print('Error logging in: {0}'.format(e.args[0]))
            sys.exit()

        results = get_data_from_reactome(filename)
        if not results:
            print('No wikidata entries made')
            sys.exit()
        try:
            create_or_update_items(logincreds, results)
        except Exception as e:
            print('Error writing results: {0}'.format(e.args[0]))
            sys.exit()

        print('Upload successfully completed')

if __name__ == '__main__':
    main(sys.argv)

