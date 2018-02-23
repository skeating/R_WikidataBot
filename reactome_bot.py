__author__ = 'Sarah Keating'

from wikidataintegrator import wdi_core, wdi_property_store, wdi_helpers
import add_entry
import global_variables
from time import gmtime, strftime
from SPARQLWrapper import SPARQLWrapper, JSON
import display_item
import os


class ReactomeBot:
    def __init__(self, write_to_wd):
        """
        Class to run the Reactome Bot
        """
        self.writing_to_WD = write_to_wd
        self.fast_run = True

        # variables for the wikidata run
        self.logincreds = None
        self.fast_run_base_filter = dict({'P3937': '', 'P703': 'Q15978631'})
        self.wikidata_sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
        self.wikidata_sparql.setReturnFormat(JSON)

        self.current_species = 'Q15978631'

        # tell the properties about reactome ID
        wdi_property_store.wd_properties['P3937'] = {
            'datatype': 'string',
            'name': 'Reactome ID',
            'domain': ['pathways'],
            'core_id': True
        }

    @staticmethod
    def create_reference(result):
        """
        Function to create the reference that is added to many properties
        tailored for Reactome
        :param result: the single result read from Reactome
        :return: reference: list of entries for the reference section

        """
        ref_stated_in = wdi_core.WDItemID(value="Q2134522", prop_nr='P248', is_reference=True)
        str_time_now = strftime("+%Y-%m-%dT00:00:00Z", gmtime())
        ref_retrieved = wdi_core.WDTime(str_time_now, prop_nr='P813', is_reference=True)
        ref_reactome = wdi_core.WDString(result['pwId']['value'], prop_nr='P3937', is_reference=True)
        if ref_reactome is None:
            reference = [ref_stated_in, ref_retrieved]
        else:
            reference = [ref_stated_in, ref_retrieved, ref_reactome]
        return reference

    def create_or_update_items(self, results, dataType):
        """
        Function to loop through all results and create or update a wikidata item
        :param results: the dictionary of results read from Reactome
        :return: None
        """
        if results is None:
            return
        for result in results["results"]["bindings"]:
            property_list = dict()
            if result['pwLabel']['value'] == '':
                continue
            self.create_or_update_item(result, property_list, dataType)

    def write_to_wikidata(self, property_list, result):
        """
        Function to write the wikidata item
        :param property_list: the properties to be used for this item
        :param result: a single entry result from Reactome
        :return:
        """
        data2add = []
        for key in property_list.keys():
            for statement in property_list[key]:
                data2add.append(statement)
        wdpage = wdi_core.WDItemEngine(item_name=result["pwLabel"]["value"], data=data2add,
                                       server=global_variables.server,
                                       domain="pathway", fast_run=self.fast_run,
                                       fast_run_base_filter=self.fast_run_base_filter)
        wdpage.set_label(result["pwLabel"]["value"])
        wdpage.set_description(result['pwDescription']['value'])

        if self.writing_to_WD and self.logincreds:
            item_id_value = 0
            try:
                item_id_value = wdpage.write(self.logincreds)

                if item_id_value != 0:
                    global_variables.edited_wd_pages.append(item_id_value)
                    print('https://www.wikidata.org/wiki/{0}'.format(item_id_value))
            except Exception as e:
                wdi_core.WDItemEngine.log("ERROR",
                                          wdi_helpers.format_msg(item_id_value, 'P3937', None, str(e), type(e)))
                print('caught exception' + str(e))
        else:
            d = display_item.DisplayItem(wdpage.get_wd_json_representation(), global_variables.server)
            d.show_item()
            print('{0}'.format(result['pwLabel']['value']))

    @staticmethod
    def output_report():
        """
        Function to write a report detailing any missing wikidata entries
        Creates a file logs/wikidata_update_{time}.csv
        :return:
        """
        if not os.path.exists('logs'):
            os.makedirs('logs')
        timestringnow = gmtime()
        filename = 'logs/wikidata_update_{0}-{1}-{2}.csv'.format(timestringnow[0], timestringnow[1], timestringnow[2])
        # pmidadd = 'pmids.bat'
        # fp = open(pmidadd, 'w')
        f = open(filename, 'w')
        f.write('missing pmids,')
        for pmid in global_variables.used_wd_ids['pmid']:
            f.write('{0},'.format(pmid))
        #     if pmid != '""':
        #         length = len(pmid)
        #         short = pmid[1:length-1]
        #          fp.write('C:\curl\src\curl.exe --header \"Authorization: '
        #     'Token 6277c658b5e42679f8b0f88309358ec1e0265533\" '
        #     'tools.wmflabs.org/fatameh/token/pmid/add/{0}\n'.format(short))
        f.write('\n')
        f.write('missing go terms,')
        for term in global_variables.used_wd_ids['goterms']:
            f.write('{0},'.format(term))
        f.write('\n')
        f.write('missing reactome,')
        for react in global_variables.used_wd_ids['reactome']:
            f.write('{0},'.format(react))
        f.write('\n')
        f.write('missing proteins,')
        for id in global_variables.used_wd_ids['proteins']:
            f.write('{0},'.format(id))
        f.write('\n')
        f.write('missing chebi,')
        for id in global_variables.used_wd_ids['chebi']:
            f.write('{0},'.format(id))
        f.write('\n')
        f.write('wikidata entries,')
        for id in global_variables.edited_wd_pages:
            f.write('{0},'.format(id))
        f.write('\n')
        f.close()
    
    def set_logincreds(self, logincreds):
        """
        Sets the wikidata login credentials
        :param logincreds:
        :return: None
        """
        self.logincreds = logincreds

    def create_or_update_item(self, result, property_list, data_type):
        """
        Function to create or update a pathway item in wikidata
        :param result: a single result entry for a Reactome Pathway
        :param property_list: the list of wikidata properties to be populated
        :return: None
        """
        if result['pwLabel']['value'] == '':
                return False
        reference = self.create_reference(result)
        if data_type == 'pathway':
            print('Creating/updating pathway: ' + result["pwId"]["value"])
            add_pathway = add_entry.AddPathway(result['pwId']['value'], self.wikidata_sparql, reference,
                                               self.current_species)
            add_pathway.add_pathway(property_list, result)
        elif data_type == 'entity':
            print('Creating/updating entity: ' + result["pwId"]["value"])
            add_entity = add_entry.AddEntity(result['pwId']['value'], self.wikidata_sparql, reference,
                                               self.current_species)
            add_entity.add_entity(property_list, result)
        self.write_to_wikidata(property_list, result)

    # future proofing functions to allow code to set species
    def set_species(self, index):
        """
        Sets the species being used for import
        :param index: integer index in supported list
        :return:
        """
        self.current_species = global_variables.supported_species[index]['WDItem']
