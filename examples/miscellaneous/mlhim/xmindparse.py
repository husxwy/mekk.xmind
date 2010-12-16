from mekk.xmind import XMindDocument

xmind = XMindDocument.open("openEHR-EHR-OBSERVATION.apgar.v1.xmind")

ccd_sheet = xmind.get_first_sheet()

ccd = ccd_sheet.get_root_topic()
print "CCD Title:       ", ccd.get_title()
print "CCD Template Id: ", ccd.get_correlation_id()
# here we need to compare the id to know which CCD template is being used.

for cl in ccd.get_subtopics():  #current level
    if cl.get_title() == 'definition':
        x = True
        while x:
            nl = cl.get_suptopics() # next level generator
            for cl in nl:
                print cl.get_title()
                if cl is None:
                    x = False
            
    
