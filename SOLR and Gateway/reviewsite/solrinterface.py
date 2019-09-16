import requests
import re
import urllib

def do_query(params, collection, port="8983"):
    param_arg = "&".join(list(map(lambda p: f"{p[0]}={p[1]}", list(params.items()))))

    query_string = f"http://localhost:{port}/solr/{collection}/select"

    r = requests.get(query_string, param_arg)
    if (r.status_code == 200):
        return r.json()
    else:
        raise Exception("Request Error: {}".format(r.status_code))

def get_review_details(review_id):
    response = do_query({"q" : f"id:{review_id}"}, "reviews")["response"]
    if response["numFound"] == 0:
        raise Exception("No review found with id {}".format(review_id))
    if response["numFound"] > 1:
        raise Exception("More than one review found with asin {}".format(review_id))
    return response["docs"][0]

def get_product_details(asin):
    response = do_query({"q" : f"asin:{asin}"}, "products")["response"]
    if response["numFound"] == 0:
        raise Exception("No product found with asin {}".format(asin))
    if response["numFound"] > 1:
        raise Exception("More than one product found with asin {}".format(asin))
    return response["docs"][0]

def search_keywords(keywords, start=0, facetValue=None):
    params = {
        "q" : f"_text_:{keywords}",
        "start" : f"{start}",
        "facet" : "true",
        "facet.field" : "overall",
    }

    if facetValue is not None:
        params["fq"] = f"overall:{facetValue}"

    params["q"] = urllib.parse.quote(params["q"])
    return do_query(params, "reviews")

def list_records(collection):
    return do_query({"q": "*"}, collection)["response"]
