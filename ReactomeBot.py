__author__ = 'Sarah'

from wikidataintegrator import wdi_core
import DisplayItem



mfw = wdi_core.WDItemEngine(wd_item_id='Q28031545')
mfw_d = mfw.get_wd_json_representation()
d = DisplayItem.DisplayItem(mfw_d)
d.show_item()
# parsed = json.loads(mfw.get_wd_json_representation())
# print (json.dumps(parsed, indent=4, sort_keys=True))