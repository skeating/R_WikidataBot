__author__ = 'Sarah'

from wikidataintegrator import wdi_core
import json

mfw = wdi_core.WDItemEngine(wd_item_id='Q28031545')
mfw_d = mfw.get_wd_json_representation()
for x in mfw_d:
    print (x)
    for y in mfw_d[x]:
        print(y, ':', mfw_d[x][y])
# parsed = json.loads(mfw.get_wd_json_representation())
# print (json.dumps(parsed, indent=4, sort_keys=True))