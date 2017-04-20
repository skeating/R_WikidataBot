__author__ = 'Sarah'


class DisplayItem():
    def __init__(self, wd_json_dict):
        self.item = wd_json_dict

    def show_item(self):
        self.show_description()
        self.show_label()
        self.show_claims()

    def show_description(self):
        desc = self.item['descriptions']
        en_desc = desc['en']
        print('Description: ', en_desc['value'])

    def show_label(self):
        desc = self.item['labels']
        en_desc = desc['en']
        print('Label: ', en_desc['value'])

    def show_claims(self):
        claims = self.item['claims']
        print('Claims:')
        for claim_val in claims:
            print(claim_val)
            self.show_claim(claims[claim_val])
#        self.show_claim(claims['P528'])

    def show_claim(self, claim):
        for i in range(0, len(claim)):
            claim_type = 'unknown'
            claim_value = 'unknown'
            claim_property = 'unknown'
            claim_type = claim[i]['type']
            mainsnak = claim[i]['mainsnak']
            claim_property = mainsnak['property']
            if mainsnak['datatype'] == 'string':
                claim_value = self.get_string_claim(mainsnak)
            elif mainsnak['datatype'] == 'wikibase-item':
                claim_value = self.get_item_claim(mainsnak)
            else:
                print('Unexpected type {0} encountered'.format(mainsnak['datatype']))
            print('{0}: is {1} {2}'.format(claim_type, claim_property, claim_value))

    def get_item_claim(self, obj):
        item_claim = 'unknown'
        if obj['snaktype'] == 'value':
            datavalue = obj['datavalue']['value']
            item_claim = '{0}: {1}'.format(datavalue['entity-type'], datavalue['id'])
        return item_claim

    def get_string_claim(selfself, obj):
        item_claim = 'unknown'
        if obj['snaktype'] == 'value':
            datavalue = obj['datavalue']
            item_claim = '{0}: {1}'.format(datavalue['type'], datavalue['value'])
        return item_claim
