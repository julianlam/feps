# /// script
# dependencies = [
#   "markdown",
#   "beautifulsoup4",
#   "rdflib>=7.0.0",
#   "markdownify",
#   "python-frontmatter",
# ]
# ///

import markdown  # convert Markdown to HTML
import bs4  # HTML filtering
import rdflib  # load and serialize ontology graphs
from rdflib.plugins.serializers.turtle import TurtleSerializer
import json
import argparse
import pathlib
import markdownify  # convert HTML to markdown
import frontmatter  # load YAML frontmatter
import re

# TODO: consider migrating from `markdown` and maybe `frontmatter` to `markdown-it-py`?

#### Some logic to make rdflib output prettier Turtle documents.
# Most of it is commented out for now because
# I'm not sure if it is or is not actually a best practice to
# use or rely on Turtle's support for numeric literal coercion.

class CustomTurtleSerializer(TurtleSerializer):
	indentString = '\t'

	# # internal variables copied from source
	# SUBJECT = 0
	# VERB = 1
	# OBJECT = 2
	# _GEN_QNAME_FOR_DT = False

	# def label(self, node, position):
	# 	"""
	# 	Copied from source but added branch for integer literals.
	# 	Also modified variable names to make it work.
	# 	"""
	# 	if node == rdflib.namespace.RDF.nil:
	# 		return "()"
	# 	if position is self.VERB and node in self.keywords:
	# 		return self.keywords[node]
	# 	if isinstance(node, rdflib.term.Literal):
	# 		if node.datatype in [
	# 			rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer'),
	# 			rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'),
	# 		]:
	# 			return int(node)
	# 		return node._literal_n3(
	# 			use_plain=True,
	# 			qname_callback=lambda dt: self.getQName(dt, self._GEN_QNAME_FOR_DT),
	# 		)
	# 	else:
	# 		node = self.relativize(node)
	# 		return self.getQName(node, position == self.VERB) or node.n3()

	# def write(self, value):
	# 	if isinstance(value, int):
	# 		self.stream.write(str(value).encode('utf-8'))
	# 	else:
	# 		self.stream.write(value.encode(self.encoding, "replace"))

rdflib.plugin.register(
	'turtle',
	rdflib.plugin.Serializer,
	'make_definitions',
	'CustomTurtleSerializer'
)

#### Main scripting logic

# define arguments and flags
## initialize argument parser
argparser = argparse.ArgumentParser(
	formatter_class=argparse.RawTextHelpFormatter
)
## Pick the FEP by its slug
argparser.add_argument(
	'slug',
	help='The slug of the FEP for which to generate term definitions.'
)
## Allow choosing a prewritten context document to inject
argparser.add_argument(
	'-c',
	metavar='PATH_TO_CONTEXT',
	help='''Specify the path to a manually written context document.
This context document will be copied into `fep-$SLUG.jsonld`.

/!\\ Similar to `--no-generate-context`,
    except it will overwrite the @context
    instead of preserving the existing @context.

/!\\ Implies JSON-LD output of at least @context.

''',
	default=None
)
## Output in only chosen formats
argparser.add_argument(
	'-f',
	metavar='FORMAT_NAME',
	help='''If provided, output in the given format(s) only.
Can be provided multiple times.

Available formats:
- turtle | ttl | .ttl
- rdfxml | xml | rdf/xml | .rdf
- json-ld | jsonld | .jsonld
- html+rdfa | rdfa | html | .html
- readme | markdown | md | .md

`md` does nothing if your terms use fragment ids.

Provide any other value to skip outputting to any formats.

''',
	default=[],
	action='append'
)
## Skip auto-generation of context and preserve existing @context
argparser.add_argument(
	'-n',
	'--no-generate-context',
	help='''Disable automatic context generation.
If `-c` is not provided, then `fep-xxxx.jsonld` will be read
and the existing `@context` will be preserved unless empty.
''',
	default=False,
	action='store_true'
)
args = argparser.parse_args()

# parsed args and feature flags
slug = args.slug
GENERATE_CONTEXT_FROM_TERMDEFS = not args.no_generate_context and not args.c
OUTPUT_FORMATS = [str.lower(x) for x in args.f]
PATH_TO_CONTEXT = args.c or f'fep/{slug}/fep-{slug}.jsonld'

if not OUTPUT_FORMATS:
	# is it fair to say that RDF/XML is a dying format?
	# maybe we don't need to enable it by default
	OUTPUT_FORMATS = ['turtle', 'rdfxml', 'jsonld', 'html', 'md']

OUTPUT_TURTLE = (
	'turtle' in OUTPUT_FORMATS
	or 'ttl' in OUTPUT_FORMATS
	or '.ttl' in OUTPUT_FORMATS
)
OUTPUT_RDFXML = (
	'rdfxml' in OUTPUT_FORMATS
	or 'xml' in OUTPUT_FORMATS
	or 'rdf/xml' in OUTPUT_FORMATS
	or '.rdf' in OUTPUT_FORMATS
)
OUTPUT_JSONLD = (
	'json-ld' in OUTPUT_FORMATS
	or 'jsonld' in OUTPUT_FORMATS
	or '.jsonld' in OUTPUT_FORMATS
)
OUTPUT_HTML_RDFA = (
	'html+rdfa' in OUTPUT_FORMATS
	or 'rdfa' in OUTPUT_FORMATS
	or 'html' in OUTPUT_FORMATS
	or '.html' in OUTPUT_FORMATS
)
OUTPUT_MARKDOWN_README = (
	'readme' in OUTPUT_FORMATS
	or 'markdown' in OUTPUT_FORMATS
	or 'md' in OUTPUT_FORMATS
	or '.md' in OUTPUT_FORMATS
)

# parse the FEP file for term definitions
with open(f'fep/{slug}/fep-{slug}.md', 'r') as f:
	file_contents = f.read()

html = markdown.markdown(
	file_contents,
	tab_length=47  # python-markdown hates tabs for some reason,
).replace(  # so we need to convert them back
	'                                               ',
	'\t'  # if we want to preserve tabs.
)
fep = frontmatter.loads(file_contents)

# we can define a "term definition block" in 888d as
# any element with
# - an `id` attr equal to the term name, and
# - a `resource` attr equal to the term iri
soup = bs4.BeautifulSoup(html, 'html.parser')
term_nodes = soup.find_all(id=True, resource=True)
if not term_nodes:
	exit()

# set up a fep-wide graph to contain all term definitions
fep_id = f'https://w3id.org/fep/{slug}'
g_all = rdflib.Graph(identifier=f'{fep_id}#')  # TODO: is it best practice to name this graph or leave it unnamed?
g_all.bind('as', rdflib.Namespace('https://www.w3.org/ns/activitystreams#'))
nm = rdflib.namespace.NamespaceManager(g_all)
# initialize this graph with metadata about the FEP
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('rdf:type')),
	rdflib.URIRef(nm.expand_curie('owl:Ontology'))
))
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('dcterms:identifier')),
	rdflib.Literal(fep_id, datatype=nm.expand_curie('xsd:anyURI'))
))
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('dc:rights')),
	rdflib.Literal('CC0 1.0 Universal (CC0 1.0) Public Domain Dedication', lang='en')
))
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('dcterms:license')),
	rdflib.URIRef('https://creativecommons.org/publicdomain/zero/1.0/')
))
## grab title and summary from FEP contents
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('dcterms:title')),
	rdflib.Literal(soup.find('h1').text)
))
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('dcterms:abstract')),
	rdflib.Literal(soup.find(string='Summary').parent.find_next_sibling().text)
))
## `authors`
for author in fep.get('authors', '').split(','):
	g_all.add((
		rdflib.URIRef(fep_id),
		rdflib.URIRef(nm.expand_curie('dc:creator')),
		rdflib.Literal(author.strip())
	))
## `status`
## `dateReceived`
g_all.add((
	rdflib.URIRef(fep_id),
	rdflib.URIRef(nm.expand_curie('dcterms:dateSubmitted')),
	rdflib.Literal(fep.get('dateReceived'))
))
## `dateWithdrawn`
## `dateFinalized`
## `trackingIssue`
## `discussionsTo`
## `relatedFeps`
for related in fep.get('relatedFeps', '').split(','):
	if related:
		related_slug = related.strip().lower().removeprefix('fep-')
		g_all.add((
			rdflib.URIRef(fep_id),
			rdflib.URIRef(nm.expand_curie('dcterms:relation')),
			rdflib.URIRef(f'https://w3id.org/fep/{related_slug}')
		))
## `replaces`
for replaces in fep.get('replaces', '').split(','):
	if replaces:
		replaces_slug = related.strip().lower().removeprefix('fep-')
		g_all.add((
			rdflib.URIRef(fep_id),
			rdflib.URIRef(nm.expand_curie('dcterms:replaces')),
			rdflib.URIRef(f'https://w3id.org/fep/{replaces_slug}')
		))
## `replacedBy`
for replacedBy in fep.get('replacedBy', '').split(','):
	if replacedBy:
		replacedBy_slug = related.strip().lower().removeprefix('fep-')
		g_all.add((
			rdflib.URIRef(fep_id),
			rdflib.URIRef(nm.expand_curie('dcterms:isReplacedBy')),
			rdflib.URIRef(f'https://w3id.org/fep/{replacedBy_slug}')
		))

# initialize a context or read a manually written one
context = {}
if not GENERATE_CONTEXT_FROM_TERMDEFS and PATH_TO_CONTEXT:
	with open(PATH_TO_CONTEXT, 'r') as f:
		try:
			context = json.loads(f.read()).get('@context')
		except ValueError:
			pass

# process all term definitions that we found
term_node: bs4.Tag
for term_node in term_nodes:

	## extract name and iri
	term_name = term_node.attrs.get('id')
	term_iri = term_node.attrs.get('resource')

	## make a subfolder for each term if not using frag-ids
	SEPARATE_TERM_DEFINITIONS = '#' not in term_iri
	if SEPARATE_TERM_DEFINITIONS:
		pathlib.Path(f'fep/{slug}/{term_name}').mkdir(exist_ok=True)

	## save RDFa directly as term/term.html
	if SEPARATE_TERM_DEFINITIONS and OUTPUT_HTML_RDFA:
		with open(f'fep/{slug}/{term_name}/{term_name}.html', 'w') as f2:
			f2.write(f'<!DOCTYPE html>\n<html>\n<head>\n<title>{term_name}</title>\n</head>\n<body>\n' + re.sub(r'h\d{1}\>', r'h1>', str(term_node)) + '\n</body>\n</html>')
	
	## extract examples for further processing later
	examples = [x.extract() for x in term_node.find_all('pre')]

	## write term/README.md for Codeberg repo
	if SEPARATE_TERM_DEFINITIONS and OUTPUT_MARKDOWN_README:
		with open(f'fep/{slug}/{term_name}/README.md', 'w') as f2:
			f2.write(f'# {term_name}\n')
			dl_pairs = zip(
				term_node.find('dl').find_all('dt'),
				term_node.find('dl').find_all('dd')
			)
			for dt, dd in dl_pairs:
				f2.write(f'\n{dt.text}\n: {markdownify.markdownify(dd.decode_contents(), escape_misc = False)}\n')
			if examples:
				f2.write('\n\n## Examples\n')
				for example in examples:
					example_title = example.attrs.get('title')
					example_lang = example.attrs.get('lang')
					if example_title:
						f2.write(f'\n{example_title}\n')
					f2.write(f'\n```{example_lang}' + example.code.text + '```\n')

	## convert term definition into a term graph
	### initialize the term graph
	g = rdflib.Graph()
	g.bind('as', rdflib.Namespace('https://www.w3.org/ns/activitystreams#'))
	### initialize a list of statements
	s = term_iri
	term_type = term_node.attrs.get('typeof')
	statements = [(s, 'rdf:type', term_type, None, None)]  # s,p,o,datatype,lang
	### extract statements from the term definition
	statement_nodes = term_node.find_all(property=True)
	for statement_node in statement_nodes:
		p = statement_node.attrs['property']
		o = (
			statement_node.attrs.get('resource')
			or statement_node.attrs.get('href')
			or statement_node.attrs.get('content')
			or statement_node.text
		)
		lang = statement_node.attrs.get('lang')
		datatype = statement_node.attrs.get('datatype')
		statements.append((s,p,o,datatype,lang))
	### generate triples from each statement
	for statement in statements:
		s,p,o,datatype,lang = statement
		if datatype or lang:  # Literal
			try:
				p = nm.expand_curie(p)
			except ValueError:
				pass
			try:
				if datatype:
					datatype = nm.expand_curie(datatype)
			except ValueError:
				pass
			triple = (
				rdflib.URIRef(s),
				rdflib.URIRef(p),
				rdflib.Literal(o, datatype=datatype, lang=lang)
			)
		else:  # URI reference
			try:
				p = nm.expand_curie(p)
			except ValueError:
				pass
			try:
				o = nm.expand_curie(o)
			except ValueError:
				pass
			triple = (
				rdflib.URIRef(s),
				rdflib.URIRef(p),
				rdflib.URIRef(o)
			)
		#### add the generated triple to the term graph
		g.add(triple)

	##  write term definitions from term graph
	if SEPARATE_TERM_DEFINITIONS and OUTPUT_TURTLE:
		ttl_graph = g.serialize(format='turtle')
		with open(f'fep/{slug}/{term_name}/{term_name}.ttl', 'w') as f2:
			f2.write(ttl_graph.rstrip())
	if SEPARATE_TERM_DEFINITIONS and OUTPUT_RDFXML:
		rdfxml_graph = g.serialize(format='xml')
		with open(f'fep/{slug}/{term_name}/{term_name}.rdf', 'w') as f2:
			f2.write(rdfxml_graph.rstrip())
	if SEPARATE_TERM_DEFINITIONS and OUTPUT_JSONLD:
		jsonld_graph = g.serialize(format='json-ld')
		with open(f'fep/{slug}/{term_name}/{term_name}.jsonld', 'w') as f2:
			f2.write(jsonld_graph)

	## merge term graph into fep-wide graph
	g_all += g

	## auto-generate context term definition from term definition
	if GENERATE_CONTEXT_FROM_TERMDEFS and not term_node.attrs.get('excluded'):
		options = {}
		dl_pairs = zip(
			term_node.find('dl').find_all('dt'),
			term_node.find('dl').find_all('dd')
		)
		range_definition = [y for (x,y) in dl_pairs if x.text == 'Range']
		if range_definition:
			range_definition = range_definition[0]
		### @type: some iri
		if range_definition and range_definition.attrs.get('resource'):
			type_iri = range_definition.attrs.get('resource')
			#### i think we only care about xsd types? TODO: re-evaluate this assumption
			if type_iri.startswith('xsd'):
				options = options | {'@type': nm.expand_curie(type_iri)}
		### @type: @id
		if range_definition and '@id' in range_definition.text:
			options = options | {'@type': '@id'}
		### @type: @vocab
		if range_definition and '@vocab' in range_definition.text:
			options = options | {'@type': '@vocab'}
		### @container: @set
		if range_definition and '@set' in range_definition.text:
			options = options | {'@container': '@set'}
		### @container: @list
		if range_definition and '@list' in range_definition.text:
			options = options | {'@container': '@list'}
		### more advanced stuff? idk
		## anyway, make either an expanded or simple definition.
		if options:  # expanded term definition
			term_definition = {
				'@id': f'{term_iri}'
			}
			term_definition = term_definition | options
		else:  # simple term definition
			term_definition = term_iri
		## now make the term mapping
		term_mapping = {
			f'{term_name}': term_definition
		}
		## and then merge it into the context mapping.
		context = context | term_mapping

# write fep-wide definitions from fep-wide graph

if OUTPUT_TURTLE:
	fep_ttl = g_all.serialize(format='turtle')
	with open(f'fep/{slug}/fep-{slug}.ttl', 'w') as f:
		f.write(fep_ttl)

if OUTPUT_RDFXML:
	fep_rdfxml = g_all.serialize(format='xml')
	with open(f'fep/{slug}/fep-{slug}.rdf', 'w') as f:
		f.write(fep_rdfxml)

if OUTPUT_JSONLD or GENERATE_CONTEXT_FROM_TERMDEFS:
	fep_jsonld = g_all.serialize(format='json-ld', context=context)
	if not OUTPUT_JSONLD:
		fep_jsonld = rdflib.Graph().serialize(format='json-ld', context=context)
		fep_jsonld = json.loads(fep_jsonld)
		if '@graph' in fep_jsonld:
			del fep_jsonld['@graph']
		fep_jsonld = json.dumps(fep_jsonld, indent='\t')
	with open(f'fep/{slug}/fep-{slug}.jsonld', 'w') as f:
		f.write(fep_jsonld)