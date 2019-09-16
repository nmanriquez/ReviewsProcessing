import os
import urllib
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from reviewsite.forms import ReviewSearchForm
from reviewsite.solrinterface import get_product_details, get_review_details, search_keywords, list_records

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)

	app.config.from_mapping(
		SECRET_KEY='dev',
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	@app.route('/', methods=['GET'])
	@app.route('/<name>',methods=['GET'])
	def index(name=""):
		products = list_records("products")
		reviews = list_records("reviews")
		return render_template('index.html', products=products, reviews=reviews)

	@app.route('/review/search',methods=['GET','POST'])
	def searchForm():
		form = ReviewSearchForm()
		if request.method =='GET':
			return render_template("reviewsearch.html",form=form)
		elif not form.validate():
			return render_template("reviewsearch.html",form=form)
		else:
			return redirect(url_for('reviewResults', query=form.keywords.data, start=0))

	@app.route('/review/results')
	def reviewResults():
		start = request.args.get('start')
		query = request.args.get('query')
		facetValue = request.args.get('facetValue')
		response = search_keywords(query, start, facetValue)

		page_info = {"start": response["response"]["start"], "numFound": response["response"]["numFound"], "numShown": len(response["response"]["docs"])}
		if(len(response["spellcheck"]["collations"]) > 0):
			page_info["spellcheck"] = response["spellcheck"]["collations"][1][7:]

		reviews = response["response"]["docs"]

		for review in reviews:
			asin = review["asin"]

			try:
				product = get_product_details(asin)
			except Exception as e:
				product = {}
			review["product"] = product

		facet_dict = {}
		facet_counts = response["facet_counts"]
		facet_iterator = iter(facet_counts["facet_fields"]["overall"])
		for score in facet_iterator:
			counts = next(facet_iterator)
			facet_dict[score] = counts
		return render_template('searchresults.html', reviews=reviews, page_info=page_info, query=query, facetValue=facetValue, facet_dict=facet_dict)

	@app.route('/product/detail', methods=['GET'])
	def productDetail():
		asin = request.args.get("asin")
		product = get_product_details(asin)
		return render_template('productdetails.html', product=product)

	@app.route('/review/detail', methods=['GET'])
	def reviewDetail():
		review_id = request.args.get("id")
		review = get_review_details(review_id)

		asin = review["asin"]
		product = get_product_details(asin)
		return render_template('reviewdetails.html', review=review, product=product)

	return app
