import sys
from eulfedora.server import Repository
from argparse import ArgumentParser

HOSTURL = 'http://digital.lib.niu.edu'
fedoraUser = 'xxx'
fedoraPass = 'xxx'

repo = Repository(root='%s:8080/fedora/' % HOSTURL, username='%s' % fedoraUser, password='%s' % fedoraPass)

def getObjects(collection):
    # Query for page pids
    pids = []
    results = repo.risearch.sparql_query("""select distinct ?pid ?model where {?pid <fedora-rels-ext:isMemberOfCollection>+ <info:fedora/%s> ;
                                            <fedora-model:hasModel> ?model .
                                            FILTER (?model = <info:fedora/niu-amarch:cmodel> ||
                                            ?model = <info:fedora/niu-objects:cmodel> ||
                                            ?model = <info:fedora/islandora:sp_pdf> ||
                                            ?model = <info:fedora/islandora:bookCModel> ||
                                            ?model = <info:fedora/islandora:sp_basic_image> ||
                                            ?model = <info:fedora/islandora:sp_large_image_cmodel> ||
                                            ?model = <info:fedora/islandora:sp-audioCModel> ||
                                            ?model = <info:fedora/islandora:sp_videoCModel> ||
                                            ?model = <info:fedora/islandora:compoundCModel>)}""" % collection)
    for row in results:
        pids.append(row['pid'].replace('info:fedora/', ''))
  
    return pids

def main(argv):
    # Retreive books from genre
    objects = getObjects(args.set)
 
    file = open (args.out, "w")
    file.write("""<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
<responseDate>2015-10-11T00:35:52Z</responseDate>
<ListRecords>
""")
    fail = []
    for o in objects:
        print "Currently processing document: %s" % o
        try:
            obj = repo.get_object(o)
            mods = obj.getDatastreamObject('MODS').content
            file.write("""<record>
       <header>
        <identifier>%s</identifier>
        <datestamp>2015-03-17T18:33:21Z</datestamp>
       </header>
       <metadata>
       %s
       </metadata>
       </record>
    """ % (o, mods.serialize(pretty=True)))
        except:
            print "\n\n------WARNING: %s failed----\n\n" % o
            fail.append(o)
            continue
     
    file.write("""</ListRecords>
</OAI-PMH>
""")
    file.close()
    print "Failed to harvest records for the following objects:\n%s" % fail
 
       
if __name__ == '__main__':
 
    parser = ArgumentParser()
 
    parser.add_argument("-s", "--set", dest="set", help="Identify collection to harvest.", default="islandora:root")
    parser.add_argument("-o", "--out", dest="out", help="Enter output file.", default="output.xml")
 
    args = parser.parse_args()
 
    sys.exit(main(sys.argv))
