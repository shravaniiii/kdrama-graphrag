import pandas as pd
from neo4j import GraphDatabase
import os
import ast

URI = 'neo4j+s://61885e62.databases.neo4j.io'
USERNAME = '61885e62'
PASSWORD = '4ltUzsQcRYiETIDh7QF-cYBYY7TxZWyr-MLxJimVI8Q'

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def load_dramas():
    df = pd.read_csv('data_raw/korean_dramas_clean.csv')
    print(f'Loading {len(df)} dramas into Neo4j...')
    
    with driver.session() as session:
        # Clear existing data first
        session.run('MATCH (n) DETACH DELETE n')
        print('Cleared existing data')
        
        for i, row in df.iterrows():
            try:
                # Create Drama node
                session.run("""
                    MERGE (d:Drama {name: $name})
                    SET d.rating = $rating,
                        d.year = $year,
                        d.episodes = $episodes,
                        d.synopsis = $synopsis,
                        d.viewers = $viewers,
                        d.popularity = $popularity,
                        d.director = $director,
                        d.screenwriter = $screenwriter
                """,
                    name=str(row['name']),
                    rating=float(row['rating']) if pd.notna(row['rating']) else 0.0,
                    year=str(row['year']) if pd.notna(row['year']) else '',
                    episodes=str(row['episodes']) if pd.notna(row['episodes']) else '',
                    synopsis=str(row['content'])[:500] if pd.notna(row['content']) else '',
                    viewers=float(row['no_of_viewers']) if pd.notna(row['no_of_viewers']) else 0.0,
                    popularity=float(row['popularity']) if pd.notna(row['popularity']) else 0.0,
                    director=str(row['director']) if pd.notna(row['director']) else '',
                    screenwriter=str(row['screenwriter']) if pd.notna(row['screenwriter']) else ''
                )

                # Create Genre nodes
                if pd.notna(row['genres']):
                    for genre in str(row['genres']).split(','):
                        genre = genre.strip()
                        if genre:
                            session.run("""
                                MERGE (g:Genre {name: $genre})
                                MERGE (d:Drama {name: $name})
                                MERGE (d)-[:HAS_GENRE]->(g)
                            """, genre=genre, name=str(row['name']))

                # Create Trope nodes from tags
                if pd.notna(row['tags']):
                    for tag in str(row['tags']).split(','):
                        tag = tag.strip()
                        if tag:
                            session.run("""
                                MERGE (t:Trope {name: $tag})
                                MERGE (d:Drama {name: $name})
                                MERGE (d)-[:HAS_TROPE]->(t)
                            """, tag=tag, name=str(row['name']))

                # Create Actor nodes from main_role
                if pd.notna(row['main_role']):
                    for actor in str(row['main_role']).split(','):
                        actor = actor.strip()
                        if actor and len(actor) > 2:
                            session.run("""
                                MERGE (a:Actor {name: $actor})
                                MERGE (d:Drama {name: $name})
                                MERGE (a)-[:ACTED_IN]->(d)
                            """, actor=actor, name=str(row['name']))

                if i % 100 == 0:
                    print(f'  Loaded {i}/{len(df)} dramas...')

            except Exception as e:
                print(f'  Error on {row["name"]}: {e}')
                continue

    print(f'\nDone! Loaded {len(df)} dramas into Neo4j')

if __name__ == "__main__":
    load_dramas()
    driver.close()
    