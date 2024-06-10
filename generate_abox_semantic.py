from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF
import pandas as pd
import random

# Load the TBox definition
tbox_path = 'TBOX.ttl'
g = Graph()
g.parse(tbox_path, format='ttl')

# Paths to the actual CSV files
authors_csv_path = 'data/SemanticScholar/authors.csv'
papers_csv_path = 'data/SemanticScholar/papers_details_enriched.csv'
affiliations_csv_path = 'data/SemanticScholar/affiliations.csv'
author_affiliations_csv_path = 'data/SemanticScholar/affiliated_with.csv'
cited_by_csv_path = 'data/SemanticScholar/citations.csv'
written_by_csv_path = 'data/SemanticScholar/written_by_enriched.csv'
conferences_csv_path = 'data/SemanticScholar/conferences_enriched.csv'
journals_csv_path = 'data/SemanticScholar/journals_enriched.csv'
published_in_csv_path = 'data/SemanticScholar/published_in.csv'
reviews_csv_path = 'data/SemanticScholar/reviews.csv'
reviewed_by_csv_path = 'data/SemanticScholar/reviewed_by.csv'
review_on_csv_path = 'data/SemanticScholar/review_on.csv'

# Load CSV files into DataFrames
authors_df = pd.read_csv(authors_csv_path)
papers_df = pd.read_csv(papers_csv_path)
affiliations_df = pd.read_csv(affiliations_csv_path)

author_affiliations_df = pd.read_csv(author_affiliations_csv_path)
cited_by_df = pd.read_csv(cited_by_csv_path)
written_by_df = pd.read_csv(written_by_csv_path)
conferences_df = pd.read_csv(conferences_csv_path)
journals_df = pd.read_csv(journals_csv_path)
published_in_df = pd.read_csv(published_in_csv_path)
reviews_df = pd.read_csv(reviews_csv_path)
reviewed_by_df = pd.read_csv(reviewed_by_csv_path)
review_on_df = pd.read_csv(review_on_csv_path)

# Define the namespace for our data
EX = Namespace('http://www.gra.fo/schema/untitled-ekg#')
g.bind('ex', EX)

# Function to add affiliation data to the graph
def add_affiliation_to_graph(graph, affiliation_name, affiliation_type, affiliation_address, affiliation_email, affiliation_phone_number, affiliation_website):
    affiliation_uri = EX[f'Affiliation/{affiliation_name.replace(" ", "_").lower()}']
    graph.add((affiliation_uri, RDF.type, EX.Affiliation))
    graph.add((affiliation_uri, EX.affiliation_name, Literal(affiliation_name)))
    graph.add((affiliation_uri, EX.affiliation_type, Literal(affiliation_type)))
    graph.add((affiliation_uri, EX.affiliation_address, Literal(affiliation_address)))
    graph.add((affiliation_uri, EX.affiliation_email, Literal(affiliation_email)))
    graph.add((affiliation_uri, EX.affiliation_phone_number, Literal(affiliation_phone_number)))
    graph.add((affiliation_uri, EX.affiliation_website, Literal(affiliation_website)))
    return affiliation_uri


# Function to determine if a person is a reviewer based on author_id
def is_reviewer(author_id):
    return author_id in reviewed_by_df['author_id'].values

# Function to add individual data to the graph, with distinct URIs for authors and reviewers
def add_author_to_graph(graph, individual_id, author_name, author_email):
    # Determine if the individual is a reviewer
    if is_reviewer(individual_id):
        individual_uri = EX[f'Reviewer/{individual_id}']
        graph.add((individual_uri, RDF.type, EX.Reviewer))
    else:
        individual_uri = EX[f'Author/{individual_id}']
        graph.add((individual_uri, RDF.type, EX.Author))

    graph.add((individual_uri, EX.individualId, Literal(individual_id)))
    graph.add((individual_uri, EX.author_name, Literal(author_name)))
    graph.add((individual_uri, EX.author_email, Literal(author_email)))

    return individual_uri

# Function to link authors with affiliations
def link_author_to_affiliation(graph, individual_id, affiliation_name):
    # Determine if the individual is a reviewer
    if is_reviewer(individual_id):
        individual_uri = EX[f'Reviewer/{individual_id}']
        affiliation_uri = EX[f'Affiliation/{affiliation_name.replace(" ", "_").lower()}']
        graph.add((individual_uri, EX.reviewer_affiliated_with, affiliation_uri))

    else:
        individual_uri = EX[f'Author/{individual_id}']
        affiliation_uri = EX[f'Affiliation/{affiliation_name.replace(" ", "_").lower()}']
        graph.add((individual_uri, EX.author_affiliated_with, affiliation_uri))

    
# Function to add paper data to the graph
def add_paper_to_graph(graph, paper_id, paper_title, paper_abstract, paper_year, paper_doi, author_name, author_email):
    paper_uri = EX[f'Paper/{paper_id}']
    graph.add((paper_uri, RDF.type, EX.Paper))
    graph.add((paper_uri, EX.paper_id, Literal(paper_id)))
    graph.add((paper_uri, EX.paper_title, Literal(paper_title)))
    graph.add((paper_uri, EX.paper_abstract, Literal(paper_abstract)))
    graph.add((paper_uri, EX.paper_year, Literal(paper_year, datatype='http://www.w3.org/2001/XMLSchema#integer')))
    graph.add((paper_uri, EX.paper_doi, Literal(paper_doi)))
    author_uri = EX[f'Author/{author_email.lower()}']
    graph.add((paper_uri, EX.written_by, author_uri))
    return paper_uri

# Function to add citation data to the graph
def add_citation_to_graph(graph, paper_id, reference_id, year):
    paper_uri = EX[f'Paper/{paper_id}']
    reference_uri = EX[f'Paper/{reference_id}']
    graph.add((paper_uri, EX.cited_by, reference_uri))
    graph.add((paper_uri, EX.citation_year, Literal(year, datatype='http://www.w3.org/2001/XMLSchema#integer')))

# Function to link paper authors
def link_paper_author(graph, paper_id, author_id):
    paper_uri = EX[f'Paper/{paper_id}']
    author_uri = EX[f'Author/{author_id}']
    graph.add((paper_uri, EX.written_by, author_uri))

# Define research areas
research_areas = ["Databases", "Machine Learning", "Network Security", "Artificial Intelligence"]

# Function to add research areas to the graph
def add_research_areas_to_graph(graph):
    for area in research_areas:
        area_uri = EX[f'Area/{area.replace(" ", "")}']
        graph.add((area_uri, RDF.type, EX.Area))
        graph.add((area_uri, EX.Area, Literal(area)))

# Function to randomly assign a research area URI
def assign_research_area_uri():
    area = random.choice(research_areas)
    return EX[f'Area/{area.replace(" ", "")}']



# Function to add conference data to the graph
def add_conference_to_graph(graph, name, conference_url):
    name = name.replace(" ", "")
    conference_uri = EX[f'Conference/{name}']
    graph.add((conference_uri, RDF.type, EX.Conference))
    graph.add((conference_uri, EX.conference_url, Literal(conference_url) if conference_url else Literal("")))
    
    # Link the conference to a random research area
    area_uri = assign_research_area_uri()
    graph.add((conference_uri, EX.conf_related_to, area_uri))
    
    return conference_uri

# Function to add conference edition data to the graph
def add_conference_edition_to_graph(graph, edition_ss_venue_id, edition_no, edition_year, name):
    name = name.replace(" ", "")
    conference_uri = EX[f'Conference/{name}']
    edition_uri = EX[f'Edition/{edition_ss_venue_id}']
    graph.add((edition_uri, RDF.type, EX.Edition))
    graph.add((edition_uri, EX.edition_no, Literal(edition_no, datatype='http://www.w3.org/2001/XMLSchema#integer')))
    graph.add((edition_uri, EX.published_in_conference, conference_uri))
    graph.add((edition_uri, EX.edition_year, Literal(edition_year, datatype='http://www.w3.org/2001/XMLSchema#integer')))
    return edition_uri

# Function to add journal data to the graph
def add_journal_to_graph(graph, name, journal_url):
    name = name.replace(" ", "")
    journal_uri = EX[f'Journal/{name}']
    graph.add((journal_uri, RDF.type, EX.Journal))
    graph.add((journal_uri, EX.journal_url, Literal(journal_url) if journal_url else Literal("")))

    # Link the journal to a random research area
    area_uri = assign_research_area_uri()
    graph.add((journal_uri, EX.jour_related_to, area_uri))
    
    return journal_uri

# Function to add journal volume data to the graph
def add_journal_volume_to_graph(graph, volume_ss_venue_id, volume_no, volume_year, name):
    name = name.replace(" ", "")
    journal_uri = EX[f'Journal/{name}']
    volume_uri = EX[f'Volume/{volume_ss_venue_id}']
    graph.add((volume_uri, RDF.type, EX.Volume))
    graph.add((volume_uri, EX.volume_no, Literal(volume_no, datatype='http://www.w3.org/2001/XMLSchema#integer')))
    graph.add((volume_uri, EX.published_in_journal, journal_uri))
    graph.add((volume_uri, EX.volume_ss_venue_id, Literal(volume_ss_venue_id)))
    graph.add((volume_uri, EX.volume_year, Literal(volume_year, datatype='http://www.w3.org/2001/XMLSchema#integer')))
    return volume_uri

# Function to add review data to the graph
def add_review_to_graph(graph, review_id, review_decision, review_date, review_abstract):
    review_uri = EX[f'Review/{review_id}']
    graph.add((review_uri, RDF.type, EX.Review))
    graph.add((review_uri, EX.review_id, Literal(review_id)))
    graph.add((review_uri, EX.review_decision, Literal(review_decision)))
    graph.add((review_uri, EX.review_date, Literal(review_date, datatype='http://www.w3.org/2001/XMLSchema#date')))
    graph.add((review_uri, EX.review_abstract, Literal(review_abstract)))
    return review_uri

# Function to link a paper to a review
def link_review_to_paper(graph, review_id, paper_id):
    review_uri = EX[f'Review/{review_id}']
    paper_uri = EX[f'Paper/{paper_id}']
    graph.add((review_uri, EX.reviewed_on, paper_uri))

# Function to link a review to an author (reviewer)
def link_review_to_author(graph, review_id, author_id):
    review_uri = EX[f'Review/{review_id}']
    author_uri = EX[f'Reviewer/{author_id}']
    graph.add((review_uri, EX.reviewed_by, author_uri))

def link_paper_to_venue(graph, paper_id, venue_id, conferences_df, journals_df):
    paper_uri = EX[f'Paper/{paper_id}']

    # Check if the venue_id is in the conference dataframe
    if venue_id in conferences_df['ss_venue_id'].values:
        venue_uri = EX[f'Edition/{venue_id}']
        relationship = EX.published_in_edition
    # If not in conferences, check if it's in the journal dataframe
    elif venue_id in journals_df['ss_venue_id'].values:
        venue_uri = EX[f'Volume/{venue_id}']
        relationship = EX.published_in_volume
    else:
        # If the venue_id is not found in either, assign to a random conference
        random_venue_id = random.choice(conferences_df['ss_venue_id'].values)
        venue_uri = EX[f'Edition/{random_venue_id}']
        relationship = EX.published_in_edition

    # Add the triple to the graph
    graph.add((paper_uri, relationship, venue_uri))


# Add research areas: 
add_research_areas_to_graph(g)

# Add affiliations to the graph
for _, row in affiliations_df.iterrows():
    add_affiliation_to_graph(
        g,
        row['name'],
        row['type'],
        row['address'],
        row['email'],
        row['phone_number'],
        row['website']
    )

#Add authors to the graph
for _, row in authors_df.iterrows():
    add_author_to_graph(
        g,
        row['authorId'],
        row['name'],
        row['email']
    )

# Link authors to affiliations
for _, row in author_affiliations_df.iterrows():
    link_author_to_affiliation(g, row['authorId'], row['affiliation'])

# Add papers to the graph
for _, row in papers_df.iterrows():
    add_paper_to_graph(
        g,
        row['paperId'],
        row['title'],
        row['abstract'],
        row['year'],
        row['doi'],
        row['MA_name'],
        row['MA_email']
    )

# Add citations to the graph
for _, row in cited_by_df.iterrows():
    add_citation_to_graph(
        g,
        row['paperId'],
        row['referenceId'],
        row['year']
    )

#Link papers with their authors
for _, row in written_by_df.iterrows():
    link_paper_author(
        g,
        row['paperId'],
        row['authorId']
    )

#Add conferences and their editions to the graph
for _, row in conferences_df.iterrows():
    conference_uri = add_conference_to_graph(
        g,
        row['name'],
        row['url']
    )
    add_conference_edition_to_graph(
        g,
        row['ss_venue_id'],
        row['edition'],
        row['year'],
        row['name']
    )

#Add journals and their volumes to the graph
for _, row in journals_df.iterrows():
    journal_uri = add_journal_to_graph(
        g,
        row['name'],
        row['url']
    )
    add_journal_volume_to_graph(
        g,
        row['ss_venue_id'],
        row['volume'],
        row['year'],
        row['name']
    )

#Link papers to conference editions or journal volumes
for _, row in published_in_df.iterrows():
    link_paper_to_venue(g, row['paper_id'], row['ss_venue_id'], conferences_df, journals_df)

#Add reviews to the graph
for _, row in reviews_df.iterrows():
    add_review_to_graph(
        g,
        row['review_id'],
        row['decision'],
        row['date'],
        row['abstract']
    )

#Link reviews to authors (reviewers)
for _, row in reviewed_by_df.iterrows():
    link_review_to_author(
        g,
        row['review_id'],
        row['author_id']
    )

#Link reviews to papers
for _, row in review_on_df.iterrows():
    link_review_to_paper(
        g,
        row['review_id'],
        row['paper_id']
    )

# Export the graph to Turtle format
output_ttl_path = 'Semantic-ABOX.ttl'
g.serialize(destination=output_ttl_path, format='turtle')

print(f'Graph exported to Turtle format at: {output_ttl_path}')