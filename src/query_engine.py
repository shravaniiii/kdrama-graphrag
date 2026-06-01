import asyncio
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class GraphRAGEngine:

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.global_search = None
        self.local_search = None
        self._loaded = False
        self._load_error = None

    def load(self):
        try:
            self._build_search_engines()
            self._loaded = True
            logger.info("GraphRAG engine loaded into memory")
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Engine load failed: {e}")
            raise

    def query_sync(self, question: str, method: str) -> str:
        if not self._loaded:
            raise RuntimeError(f"Engine not loaded: {self._load_error}")

        async def _run():
            if method == "global":
                result = await self.global_search.search(question)
            else:
                result = await self.local_search.search(question)
            return result.response

        return asyncio.run(_run())

    def _build_search_engines(self):
        from graphrag.config.load_config import load_config
        from graphrag.query.factory import get_global_search_engine, get_local_search_engine
        from graphrag.query.indexer_adapters import (
            read_indexer_communities,
            read_indexer_entities,
            read_indexer_relationships,
            read_indexer_reports,
            read_indexer_text_units,
        )
        from graphrag.vector_stores.lancedb import LanceDBVectorStore

        config = load_config(root_dir=self.root_dir)

        reduce_prompt_path = self.root_dir / "prompts" / "global_search_reduce_system_prompt.txt"
        reduce_prompt = reduce_prompt_path.read_text(encoding="utf-8") if reduce_prompt_path.exists() else None

        map_prompt_path = self.root_dir / "prompts" / "global_search_map_system_prompt.txt"
        map_prompt = map_prompt_path.read_text(encoding="utf-8") if map_prompt_path.exists() else None

        out = self.root_dir / "output"
        entities_df          = pd.read_parquet(out / "entities.parquet")
        communities_df       = pd.read_parquet(out / "communities.parquet")
        community_reports_df = pd.read_parquet(out / "community_reports.parquet")
        relationships_df     = pd.read_parquet(out / "relationships.parquet")
        text_units_df        = pd.read_parquet(out / "text_units.parquet")

        COMMUNITY_LEVEL = 2
        entities      = read_indexer_entities(entities_df, communities_df, COMMUNITY_LEVEL)
        relationships = read_indexer_relationships(relationships_df)
        communities   = read_indexer_communities(communities_df, community_reports_df)
        reports       = read_indexer_reports(community_reports_df, communities_df, COMMUNITY_LEVEL)
        text_units    = read_indexer_text_units(text_units_df)

        logger.info(
            f"Loaded: {len(entities)} entities, {len(relationships)} relationships, "
            f"{len(communities)} communities, {len(reports)} reports, {len(text_units)} text units"
        )

        lancedb_uri = str(self.root_dir / "output" / "lancedb")
        collection = self._detect_entity_collection(lancedb_uri)
        logger.info(f"Using LanceDB collection: {collection}")

        entity_embedding_store = LanceDBVectorStore(collection_name=collection)
        entity_embedding_store.connect(db_uri=lancedb_uri)

        self.global_search = get_global_search_engine(
            config=config,
            reports=reports,
            entities=entities,
            communities=communities,
            response_type="multiple paragraphs",
            map_system_prompt=map_prompt,
            reduce_system_prompt=reduce_prompt,
        )

        self.local_search = get_local_search_engine(
            config=config,
            reports=reports,
            text_units=text_units,
            entities=entities,
            relationships=relationships,
            covariates={},
            description_embedding_store=entity_embedding_store,
            response_type="multiple paragraphs",
        )

    @staticmethod
    def _detect_entity_collection(lancedb_uri: str) -> str:
        try:
            import lancedb
            db = lancedb.connect(lancedb_uri)
            tables = db.table_names()
            logger.info(f"LanceDB tables found: {tables}")
            for candidate in tables:
                if "entity" in candidate.lower():
                    return candidate
            if tables:
                return tables[0]
        except Exception as e:
            logger.warning(f"LanceDB detection failed: {e}")
        return "default-entity-description"


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        raise RuntimeError("Engine not initialised. Call init_engine() first.")
    return _engine


def init_engine(root_dir: str):
    global _engine
    if _engine is None:
        _engine = GraphRAGEngine(root_dir)
        _engine.load()
    return _engine