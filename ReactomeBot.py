__author__ = 'Sarah'

from wikidataintegrator import wdi_core, wdi_login
import DisplayItem
import os



# test getting data
server='test.wikidata.org'
mfw = wdi_core.WDItemEngine(wd_item_id='Q39911', server=server)
mfw_d = mfw.get_wd_json_representation()
d = DisplayItem.DisplayItem(mfw_d, server)
d.show_item()

#logincreds = wdi_login.WDLogin(user=os.environ["wd_user"], pwd=os.environ["pwd"])