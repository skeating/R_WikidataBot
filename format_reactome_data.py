__author__ = 'Sarah Keating'

import os


class ReactomeData:
    def __init__(self, species, data_type):
        self.species = species
        self.data_type = data_type

    def get_data_from_reactome(self, filename):
        if self.data_type == 'pathway':
            return self.get_pathway_data_from_reactome(filename)
        elif self.data_type == "entity":
            return self.get_entity_data_from_reactome(filename)
        elif self.data_type == "reaction":
            return self.get_reaction_data_from_reactome(filename)
        else:
            return []

    @staticmethod
    def parse_list_references(reference):
        length = len(reference)
        modified_ref = ''
        if reference.startswith('[') and reference.endswith(']'):
            modified_ref = reference[1:length-1]
        return modified_ref.split(';')

    def get_pathway_data_from_reactome(self, filename):
        """
        This function creates a JSON representation of the Reactome data from a precise csv export
        this emulates the results of the wikipathways query so common code can be used

        If a filename is not given it will look for the default file

        The form of the form of the csv file is:

        species,stableId,type,name,description,[publication;publication;...],goterm,[part1;part2],[partof1;partof2],None

        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            print('{0} not found aborting ...'.format(filename))
            return None

        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        pathways = []
        for line in lines:
            variables = line.split(',')
            if len(variables) != 10:
                print('A line in the input csv file expects 10 comma separated entries')
                print('species,id,type,label,description,reference,goterm,haspart,ispartof,endelement')
                print('Re run WikidataExport to create an accurate file')
                return None
            else:
                species, st_id, event_type, label, description, reference, goterm, haspart, ispartof, endelement = \
                    line.split(',')
                lorefs = self.parse_list_references(reference)
                lo_haspart = self.parse_list_references(haspart)
                lo_ispartof = self.parse_list_references(ispartof)
                pathway = dict({'pwId': {'value': st_id, 'type': 'string'},
                                'pwLabel': {'value': self.remove_additional_name(label), 'type': 'string'},
                                'pwDescription': {'value': description, 'type': 'string'},
                                'publication': {'value': lorefs, 'type': 'list'},
                                'goTerm': {'value': goterm, 'type': 'string'},
                                'hasPart': {'value': lo_haspart, 'type': 'list'},
                                'isPartOf': {'value': lo_ispartof, 'type': 'list'}})
                pathways.append(pathway)
        b = dict({'bindings': pathways})
        results = dict({'results': b})
        return results

    def get_entity_data_from_reactome(self, filename):
        """
        This function creates a JSON representation of the Reactome data from a precise csv export
        this emulates the results of the wikipathways query so common code can be used

        If a filename is not given it will look for the default file

        The form of the form of the csv file is:

        species_code,entity_code,name,stableId,[part;part],complexportalid (only for complex),None

        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            print('{0} not found aborting ...'.format(filename))
            return None

        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        entities = []
        for line in lines:
            variables = line.split(',')
            if len(variables) != 6 and len(variables) != 7:
                print('A line in the input csv file expects 6/7 comma separated entries')
                print('species_code,entity_code,stableId,name,[part;part],'
                      'complexportalid (only for complex),endelement')
                print('Re run WikidataExport to create an accurate file')
                return None
            else:
                portal_id = ''
                if len(variables) == 6:
                    species, entitytype, st_id, label, haspart, endelement = line.split(',')
                else:
                    species, entitytype, st_id, label, haspart, portal_id, endelement = line.split(',')
                if portal_id == 'None':
                    portal_id = ''
                lo_haspart = self.parse_list_references(haspart)

                description = ''
                if entitytype == 'COMP':
                    description = 'Macromolecular complex'
                elif entitytype == 'DS':
                    description = 'Defined set from Reactome'
                elif entitytype == 'CS':
                    description = 'Candidate set from Reactome'
                elif entitytype == 'OS':
                    description = 'Open set from Reactome'

                entity = dict({'pwId': {'value': st_id, 'type': 'string'},
                               'pwLabel': {'value': label, 'type': 'string'},
                               'pwDescription': {'value': description, 'type': 'string'},
                               'hasPart': {'value': lo_haspart, 'type': 'list'},
                               'entitytype': entitytype, 'cportal': portal_id})
                entities.append(entity)
        b = dict({'bindings': entities})
        results = dict({'results': b})
        return results

    def get_reaction_data_from_reactome(self, filename):
        """
        This function creates a JSON representation of the Reactome data from a precise csv export
        this emulates the results of the wikipathways query so common code can be used

        If a filename is not given it will look for the default file

        The form of the form of the csv file is:

        species_code,stableId,eventType,Name,Description,[publication;publication;..],goterm,
          [haspart_input;haspart_input], [haspart_output;], [haspart_mod;..],[partof],None

        :param filename:
        :return:
        """
        if not os.path.isfile(filename):
            print('{0} not found aborting ...'.format(filename))
            return None

        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        pathways = []
        for line in lines:
            variables = line.split(',')
            if len(variables) != 12:
                print('A line in the input csv file expects 10 comma separated entries')
                print('species,id,type,label,description,reference,goterm,ispartof,inputs, outputs, modifiers,endelement')
                print('Re run WikidataExport to create an accurate file')
                return None
            else:
                species, st_id, event_type, label, description, reference, goterm, \
                inputs, outputs, mods, ispartof, endelement = line.split(',')
                lorefs = self.parse_list_references(reference)
                lo_hasinput = self.parse_list_references(inputs)
                lo_hasoutput = self.parse_list_references(outputs)
                lo_hasmod = self.parse_list_references(mods)
                lo_ispartof = self.parse_list_references(ispartof)
                pathway = dict({'pwId': {'value': st_id, 'type': 'string'},
                                'pwLabel': {'value': label, 'type': 'string'},
                                'pwDescription': {'value': description, 'type': 'string'},
                                'publication': {'value': lorefs, 'type': 'list'},
                                'goTerm': {'value': goterm, 'type': 'string'},
                                'inputs': {'value': lo_hasinput, 'type': 'list'},
                                'outputs': {'value': lo_hasoutput, 'type': 'list'},
                                'mods': {'value': lo_hasmod, 'type': 'list'},
                                'isPartOf': {'value': lo_ispartof, 'type': 'list'}})
                pathways.append(pathway)
        b = dict({'bindings': pathways})
        results = dict({'results': b})
        return results
