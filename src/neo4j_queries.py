from neo4j import GraphDatabase
import os

URI = os.getenv("NEO4J_URI", "neo4j+s://61885e62.databases.neo4j.io")
USERNAME = os.getenv("NEO4J_USERNAME", "61885e62")
PASSWORD = os.getenv("NEO4J_PASSWORD", "4ltUzsQcRYiETIDh7QF-cYBYY7TxZWyr-MLxJimVI8Q")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def get_similar_dramas(title: str, limit: int = 5):
    with driver.session() as session:
        result = session.run("""
            MATCH (d1:Drama {name: $name})-[:HAS_TROPE]->(t:Trope)<-[:HAS_TROPE]-(d2:Drama)
            WHERE d1 <> d2
            WITH d2, COUNT(t) as shared
            ORDER BY shared DESC LIMIT $limit
            RETURN d2.name as title, shared as shared_tropes
        """, name=title.lower(), limit=limit)
        return [{"title": r["title"], "shared_tropes": r["shared_tropes"]} for r in result]

def get_dramas_by_trope(trope: str, limit: int = 10):
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Trope {name: $trope})<-[:HAS_TROPE]-(d:Drama)
            RETURN d.name as title, d.rating as rating
            ORDER BY d.rating DESC LIMIT $limit
        """, trope=trope, limit=limit)
        return [{"title": r["title"], "rating": r["rating"]} for r in result]

def get_actor_dramas(actor: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Actor {name: $actor})-[:ACTED_IN]->(d:Drama)
            RETURN d.name as title, d.rating as rating, d.year as year
            ORDER BY d.rating DESC
        """, actor=actor)
        return [{"title": r["title"], "rating": r["rating"], "year": r["year"]} for r in result]

def get_top_tropes(limit: int = 15):
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Trope)<-[:HAS_TROPE]-(d:Drama)
            WITH t, COUNT(d) as n
            ORDER BY n DESC LIMIT $limit
            RETURN t.name as trope, n as count
        """, limit=limit)
        return [{"trope": r["trope"], "count": r["count"]} for r in result]