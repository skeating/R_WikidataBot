__author__ = 'Sarah Keating'

import os


class ReactomeData:
    def __init__(self, species, data_type):
        self.species = species
        self.data_type = data_type

    def get_data_from_reactome(self, filename):
        if self.data_type == 'pathway':
            return self.get_pathway_data_from_reactome(filename)
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
                species,id,eventType,label,description,reference,goterm,haspart,ispartof,endelement = line.split(',')
                lorefs = self.parse_list_references(reference)
                lo_haspart = self.parse_list_references(haspart)
                lo_ispartof = self.parse_list_references(ispartof)
                pathway = dict({'pwId': {'value': id, 'type': 'string'},
                                'pwLabel': {'value': label, 'type': 'string'},
                                'pwDescription': {'value': description, 'type': 'string'},
                                'publication': {'value': lorefs, 'type': 'list'},
                                'goTerm': {'value': goterm, 'type': 'string'},
                                'hasPart': {'value': lo_haspart, 'type': 'list'},
                                'isPartOf': {'value': lo_ispartof, 'type': 'list'},
                                'eventType': {'value': eventType, 'type': 'string'}})
                pathways.append(pathway)
        b = dict({'bindings': pathways})
        results = dict({'results': b})
        return results
