import json
import urllib, urllib2
from keys import BING_API_KEY

def run_query(search_terms):
    # Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'

    # how many results to be returned per page
    # offset: where in the results list to start from
    results_per_page = 10
    offset = 0

    # wrap quotes around query terms -> required by Bing API
    # query then stored in variable
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # construct latter part of request URL
    # set format to JSON + other properties
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)

    # Setup auth with bing servers
    # username must be blank str
    username = ''

    # password manage to handle authentication
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)

    # create results list to populate
    results = []

    try:
        # prepare for connecting to Bing's servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # connect to server & read generated response
        response = urllib2.urlopen(search_url).read()

        # convert the string response to a python dict
        json_response = json.loads(response)

        # Loop through each returned page
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})

    except urllib2.URLError, e:
        print "Error when querying the Bing API: ", e

    # list of results
    return results

#def main():
#    inp = raw_input("enter info: ")
#    content = run_query(inp)
#    for item in content:
#        print item['title']
#
#if __name__ == '__main__':
#    main()
