from __future__ import print_function
from mekk.xmind import XMindDocument

xmind = XMindDocument.open("openEHR-EHR-OBSERVATION.apgar.v1.xmind")

ccd_sheet = xmind.get_first_sheet()

ccd = ccd_sheet.get_root_topic()
print("CCD Title:       ", ccd.get_title())
print("CCD Template Id: ", ccd.get_correlation_id())
# here we need to compare the id to know which CCD template is being used.

for top_item in ccd.get_subtopics():  #current level
    if top_item.get_title() == 'definition':
        for level2item in top_item.get_subtopics(): # next level generator
            print("* ", level2item.get_title())
            for level3item in level2item.get_subtopics():
                print("** ", level3item.get_title())
