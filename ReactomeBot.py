__author__ = 'Sarah'

from wikidataintegrator import wdi_core, wdi_login
import DisplayItem
import os
import sys



# test getting data
server='test.wikidata.org'
#server='www.wikidata.org'
prep = dict()


def show_item(id, domain=None):
    print('Item found by id: {0} domain {1}'.format(id, domain))
    wdpage = wdi_core.WDItemEngine(wd_item_id=id, server=server, domain=domain)
    d = DisplayItem.DisplayItem(wdpage.get_wd_json_representation(), server)
    d.show_item()

def show_item_by_name(name, domain=None):
    print('Item found by name: {0} domain {1}'.format(name, domain))
    try:
        wdpage = wdi_core.WDItemEngine(item_name=name, server=server, domain=domain)
        d = DisplayItem.DisplayItem(wdpage.get_wd_json_representation(), server)
        d.show_item()
    except ValueError:
        print('Cannot find item with name {0} and domain {1}'.format(name, domain))

#adds teh statements to existing item Q59496
# note it overwrites any existing statements with same property
def add_statement(logincreds):
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

def create_item(logincreds):
    prep["31"] = [wdi_core.WDUrl(value='https://www.new.xyz', prop_nr='P31')]
    data2add = []
    for key in prep.keys():
        for statement in prep[key]:
            data2add.append(statement)
            print(statement.prop_nr, statement.value)
    wdPage = wdi_core.WDItemEngine(item_name='Sarah Test 5', data=data2add, domain='pathway', server=server)
    wdPage.set_label('Sarah Test 5')
    wdPage.set_description('my last test')
    return wdPage.write(login=logincreds, edit_summary='adding label/description')


def main(args):
    logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
#   id = create_item(logincreds)
    id = add_statement(logincreds)
    print (id)
#     name = 'Citric acid cycle (TCA cycle)'
#     id = 'Q28031545'
#     domain='pathway'
# #    print (id)
#
    id = 'Q58879'
    show_item(id)
#     print('\n')
#     show_item_by_name(name)
#     print('\n')
#     show_item(id, domain)
#     print('\n')
#     show_item_by_name(name, domain)

if __name__ == '__main__':
    main(sys.argv)
