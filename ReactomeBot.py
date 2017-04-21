__author__ = 'Sarah'

from wikidataintegrator import wdi_core, wdi_login
import DisplayItem
import os
import sys



# test getting data
server='test.wikidata.org'
#server='www.wikidata.org'
prep = dict()


def show_item(id):
    mfw = wdi_core.WDItemEngine(wd_item_id=id, server=server, search_only=True)
    d = DisplayItem.DisplayItem(mfw.get_wd_json_representation(), server)
    d.show_item()

def add_statement(logincreds):
    prep["P703"] = [wdi_core.WDItemID(value="fff", prop_nr='P703')]
    data2add = []
    for key in prep.keys():
        for statement in prep[key]:
            data2add.append(statement)
            print(statement.prop_nr, statement.value)
    wdPage = wdi_core.WDItemEngine(item_name='Sarah Test', server=server, item_data=data2add, domain='any')
    wdPage.set_description('yet another new test page')
    wdPage.set_label('Sarah Test 3')
    return wdPage.write(login=logincreds, edit_summary='adding a claim')

def main(args):
    logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
    id = add_statement(logincreds)
    show_item(id)

if __name__ == '__main__':
    main(sys.argv)
