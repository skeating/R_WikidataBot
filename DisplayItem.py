__author__ = 'Sarah'

from wikidataintegrator import wdi_core


class DisplayItem():
    '''
    Class to display the content of the resulting Wikidata page
    takes the json representation and resolves links etc
    '''
    def __init__(self, wd_json_dict, server):
        self.item = wd_json_dict
        self.server = server

    def show_item(self):
        self.show_label()
        self.show_description()
        self.show_claims()

    def show_description(self):
        if 'descriptions' not in self.item:
            value = 'No descriptions at all'
        else:
            desc = self.item['descriptions']
            value = 'No English Description'
            if 'en' in desc:
                en_desc = desc['en']
                if 'value' in en_desc:
                    value = en_desc['value']
        print('Description: ', value)

    def show_label(self):
        if 'labels' not in self.item:
            value = 'No labels at all'
        else:
            desc = self.item['labels']
            value = 'No English Label'
            if 'en' in desc:
                en_desc = desc['en']
                if 'value' in en_desc:
                    value = en_desc['value']
        print('Label: ', value)

    def show_claims(self):
         if 'claims' not in self.item:
            print('No claims field')
         else:
            claims = self.item['claims']
            print('Claims:')
            for claim_val in claims:
                self.show_claim(claims[claim_val])

    def show_claim(self, claim):
        for i in range(0, len(claim)):
            # just for sanity
            if 'type' not in claim[i] or 'mainsnak' not in claim[i]:
                continue
            claim_type = claim[i]['type']
            [claim_property, claim_value] = self.get_property_value(claim[i]['mainsnak'])
            print('{0}: {1} {2}'.format(claim_type, self.get_label(claim_property), claim_value))
            if 'qualifiers-order' in claim[i] and 'qualifiers' in claim[i]:
                self.write_qualifiers(claim[i])
                if 'references' in claim[i]:
                    self.write_references(claim[i])

    def write_qualifiers(self, claim):
        for qual in claim['qualifiers-order']:
            self.show_qualifier(claim['qualifiers'][qual])

    def write_references(self, claim):
        for ref in claim['references']:
            self.show_reference(ref)

    def show_reference(self, reference):
        for qual in reference['snaks-order']:
            self.show_qualifier(reference['snaks'][qual], claim_type='reference')

    def show_qualifier(self, claim, claim_type='qualifier'):
        for i in range(0, len(claim)):
            [claim_property, claim_value] = self.get_property_value(claim[i])
            print('{0}: {1} {2}'.format(claim_type, self.get_label(claim_property), claim_value))

    def get_property_value(self, obj):
        claim_property = obj['property']
        if obj['datatype'] == 'string' or obj['datatype'] == 'url':
            claim_value = self.get_string_claim(obj)
        elif obj['datatype'] == 'wikibase-item':
            claim_value = self.get_item_claim(obj)
        elif obj['datatype'] == 'time':
            claim_value = obj['datavalue']['value']['time']
        else:
            print('Unexpected type {0} encountered'.format(obj['datatype']))
            claim_value = 'No claim value'
        return[claim_property, claim_value]

    def get_item_claim(self, obj):
        item_claim = 'unknown'
        if obj['snaktype'] == 'value':
            datavalue = obj['datavalue']['value']
            item_claim = '{0}: {1}'.format(datavalue['entity-type'], self.get_label(datavalue['id']))
        return item_claim

    def get_string_claim(self, obj):
        item_claim = 'unknown'
        if obj['snaktype'] == 'value':
            datavalue = obj['datavalue']
            item_claim = '{0}: {1}'.format(datavalue['type'], datavalue['value'])
        return item_claim

    def get_label(self, str_value):
        mfw = wdi_core.WDItemEngine(wd_item_id=str_value, server=self.server, search_only=True)
        mfw_d = mfw.get_wd_json_representation()
        desc = mfw_d['labels']
        if 'en' in desc:
            en_desc = desc['en']
            return en_desc['value']
        else:
            return 'No English label'
