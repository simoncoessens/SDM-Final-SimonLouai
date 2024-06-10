#from journal_info_extractor import extract_journal_info

# Other imports remain the same
import json
import os
from urllib.parse import quote
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD

# Namespace and graph setup
EX = Namespace('http://www.gra.fo/schema/untitled-ekg#')
g = Graph()
g.parse('TBOX.ttl', format='ttl')
g.bind('ex', EX)

# Utility function to sanitize strings for URI creation
def sanitize_for_uri(value):
    # Encode to handle special characters
    return quote(value.replace(" ", "_"))

# Add paper data from JSON including handling journal references with extract_journal_info
def add_paper_to_graph_from_json(graph, data):
    paper_uri = EX[f'Paper/{sanitize_for_uri(data["id"])}']
    graph.add((paper_uri, RDF.type, EX.Paper))
    graph.add((paper_uri, EX.paper_id, Literal(data['id'])))
    graph.add((paper_uri, EX.paper_title, Literal(data['title'].strip())))
    graph.add((paper_uri, EX.paper_abstract, Literal(data['abstract'].strip())))
    if data['doi']:
        graph.add((paper_uri, EX.paper_doi, Literal(data['doi'])))

    # Handling authors
    author_names = data['authors'].split(", ")
    for name in author_names:
        author_uri =  EX[f'Author/{sanitize_for_uri(name)}']
        graph.add((author_uri, RDF.type, EX.Author))
        graph.add((author_uri, EX.author_name, Literal(name)))
        graph.add((paper_uri, EX.written_by, author_uri))

    # Add categories as research areas
    for category in data['categories']:
        area_uri = EX[f'Area/{sanitize_for_uri(category)}']
        graph.add((area_uri, RDF.type, EX.Area))
        graph.add((area_uri, EX.Area, Literal(category)))
        graph.add((paper_uri, EX.related_to_area, area_uri))

    # Extract and handle journal references if available
    if data['journal-ref']:
        journal_title = data['journal-ref']
        #journal_volume = extract_journal_info(data['journal-ref'])
        journal_uri = EX[f'Journal/{sanitize_for_uri(journal_title)}']
        #print(journal_title)
        #print(journal_volume)
        graph.add((journal_uri, RDF.type, EX.Journal))
        graph.add((journal_uri, EX.journal_name, Literal(journal_title)))
        #if journal_volume:
            #graph.add((journal_uri, EX.journal_volume_issue, Literal(journal_volume)))
        graph.add((paper_uri, EX.published_in_journal, journal_uri))

# Directory path and file handling
json_dir = 'data/arxiv'
for filename in os.listdir(json_dir):
    if filename.endswith('.json'):
        with open(os.path.join(json_dir, filename), 'r') as file:
            data = json.load(file)
            add_paper_to_graph_from_json(g, data)

# Serialize and save the graph
g.serialize(destination='Arxiv-ABOX.ttl', format='turtle')
print('Graph updated with arXiv data and exported to Turtle format.')
