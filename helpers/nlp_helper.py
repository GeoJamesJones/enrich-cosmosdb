import requests
import time
import json
import os
import string
import requests

# from netowlmodels import RDFitem, RDFitemGeo, RDFlinkItem, RDFeventItem, OrgDoc  # NOQA
# import netowlfuncts as nof

# ----------------------------------
#  Models for Netowl link application.
# ----------------------------------


class RDFitem:
    """Model to hold non-geo or ready to geocode items."""

    def __init__(self, rdfid, rdfvalue, timest, orgdoc, ontology, rdflinks=None):  # noqa: E501
        """Docstring."""
        self.id = rdfid
        self.links = [] if rdflinks is None else rdflinks  # list - optional
        self.value = rdfvalue
        self.timest = timest
        self.orgdoc = orgdoc
        self.type = ontology

    def set_head(self, head=""):
        """Docstring."""
        self.head = head

    def set_tail(self, tail=""):
        """Docstring."""
        self.tail = tail
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class RDFitemGeo(RDFitem):
    """Model to hold objs with lat/long already assigned."""

    def __init__(self, rdfid, rdfvalue, longt, latt, timest,
                 orgdoc, rdflinks=None):
        """Docstring."""
        self.id = rdfid
        self.links = [] if rdflinks is None else rdflinks  # list - optional
        self.value = rdfvalue
        self.lat = latt
        self.long = longt
        self.timest = timest
        self.orgdoc = orgdoc

    def set_type(self, typeofgeo):
        """Docstring."""
        self.type = typeofgeo

    def set_subtype(self, subtypegeo):
        """Docstring."""
        self.subtype = subtypegeo

    def set_link_details(self, details):
        """Docstring."""
        self.linkdetails = details

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class RDFlinkItem():
    """Model to hold link objs."""

    def __init__(self, linkid, fromid, toid, fromvalue, tovalue,
                 fromrole, torole, fromroletype, toroletype, timest):
        """Docstring."""
        self.linkid = linkid
        self.fromid = fromid
        self.toid = toid
        self.fromvalue = fromvalue
        self.tovalue = tovalue
        self.fromrole = fromrole
        self.torole = torole
        self.fromroletype = fromroletype
        self.toroletype = toroletype
        self.timest = timest


class RDFeventItem():
    """Model to hold event objs."""

    def __init__(self, eventvalue, eventid, fromid, toid, fromvalue, tovalue,
                 fromrole, torole, orgdoc, uniquets):
        """Docstring."""
        self.eventvalue = eventvalue
        self.eventid = eventid
        self.fromid = fromid
        self.toid = toid
        self.fromvalue = fromvalue
        self.tovalue = tovalue
        self.fromrole = fromrole
        self.torole = torole
        self.orgdoc = orgdoc
        self.timest = uniquets


class OrgDoc():
    """Model to maintain org docs written to graph."""

    def __init__(self, orgdoc):
        """Docstring."""
        self.orgdoc = orgdoc

# ----------------------------------
#  Functions for Netowl link application.
# ----------------------------------


def cleanup_text(intext):
    """Function to remove funky chars."""
    printable = set(string.printable)
    p = ''.join(filter(lambda x: x in printable, intext))
    g = p.replace('"', "")
    return g


def geocode_address(address):
    """Use World Geocoder to get XY for one address at a time."""
    querystring = {
        "f": "json",
        "singleLine": address}
    url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"  # noqa: E501
    response = requests.request("GET", url, params=querystring)
    p = response.text
    j = json.loads(p)
    location = j['candidates'][0]['location']  # returns first location as X, Y
    return location


def netowl_curl(infile, outpath, outextension, netowl_key):
    """Do James Jones code to query NetOwl API."""
    headers = {
        'accept': 'application/json',  # 'application/rdf+xml',
        'Authorization': netowl_key,
    }

    if infile.endswith(".txt"):
        headers['Content-Type'] = 'text/plain'
    elif infile.endswith(".pdf"):
        headers['Content-Type'] = 'application/pdf'
    elif infile.endswith(".docx"):
        headers['Content-Type'] = 'application/msword'

    # params = (
    #     ('language', 'english')
    # )

    params = {"language": "english", "text": "", "mentions": ""}

    data = open(infile, 'rb').read()
    response = requests.post('https://api.netowl.com/api/v2/_process',
                             headers=headers, params=params, data=data,
                             verify=False)

    r = response.text
    outpath = outpath
    filename = os.path.split(infile)[1]
    if os.path.exists(outpath) is False:
        os.mkdir(outpath, mode=0o777, )
    outfile = os.path.join(outpath, filename + outextension)
    open(outfile, "w", encoding="utf-8").write(r)


def make_link_list(linklist):
    """Turn linklist into string."""
    l = ""
    for u in linklist:
        l = l + " " + u
        # check size isn't bigger than 255
    o = l[1:len(l)]
    if len(o) > 255:
        o = o[:254]
    return o  # l[1:len(l)]


def create_dict_for_json(objs, listvalues):
    """Write to data dictionary for json insertion."""
    datadict = {}
    i = 0

    while i < len(listvalues):
        d = {listvalues[i]: objs[i]}
        datadict.update(d)
        i = i + 1

    return datadict


def get_head(text, headpos, numchars):
    """Return text before start of entity."""
    wheretostart = headpos - numchars
    if wheretostart < 0:
        wheretostart = 0
    thehead = text[wheretostart: headpos]
    return thehead


def get_tail(text, tailpos, numchars):
    """Return text at end of entity."""
    wheretoend = tailpos + numchars
    if wheretoend > len(text):
        wheretoend = len(text)
    thetail = text[tailpos: wheretoend]
    return thetail



