#!/usr/bin/env python3
"""
Universal Continue-style codebase searcher
Busca en el índice generado por continue_index.py
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import chromadb
import logging

# Configuración logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalContinueSearcher:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.client = None
        self.collection = None
        
    def load_index(self):
        """Carga el índice existente"""
        index_dir = self.repo_path / ".continue" / "index"
        
        if not index_dir.exists():
            logger.error(f"No index found at {index_dir}")
            return False
            
        # Cargar metadata
        metadata_path = self.repo_path / ".continue" / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.info(f"Loaded index for {self.metadata['repo_name']}")
        else:
            self.metadata = {}
            
        # Cliente ChromaDB
        self.client = chromadb.PersistentClient(path=str(index_dir))
        
        # Obtener colección
        collection_name = f"{self.repo_path.name}_codebase"
        try:
            self.collection = self.client.get_collection(collection_name)
            return True
        except Exception as e:
            logger.error(f"Error loading collection: {e}")
            return False
            
    def search(self, query: str, n_results: int = 10, 
               file_filter: str = None, extension_filter: str = None):
        """Busca en el índice"""
        if not self.collection:
            logger.error("No index loaded")
            return []
            
        # Construir filtro
        where_clause = {}
        if file_filter:
            where_clause["file_path"] = {"$regex": file_filter}
        if extension_filter:
            where_clause["extension"] = extension_filter
            
        # Buscar
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
            where=where_clause if where_clause else None
        )
        
        return results
        
    def search_files(self, query: str, n_results: int = 10):
        """Busca archivos y muestra resultados agrupados"""
        results = self.search(query, n_results * 3)  # Buscar más para agrupar
        
        # Agrupar por archivo
        files = {}
        for doc, metadata, distance in zip(
            results["documents"][0], 
            results["metadatas"][0], 
            results["distances"][0]
        ):
            file_path = metadata["file_path"]
            if file_path not in files:
                files[file_path] = {
                    "chunks": [],
                    "avg_distance": 0,
                    "chunk_count": 0,
                    "file_name": metadata["file_name"],
                    "extension": metadata["extension"]
                }
                
            files[file_path]["chunks"].append({
                "content": doc,
                "chunk_index": metadata["chunk_index"],
                "distance": distance
            })
            files[file_path]["chunk_count"] += 1
            
        # Calcular distancia promedio
        for file_data in files.values():
            if file_data["chunks"]:
                file_data["avg_distance"] = sum(c["distance"] for c in file_data["chunks"]) / len(file_data["chunks"])
                
        # Ordenar por distancia promedio
        sorted_files = sorted(files.items(), key=lambda x: x[1]["avg_distance"])
        
        # Mostrar resultados
        print(f"\n[SEARCH] Search results for: '{query}'")
        print("=" * 50)
        
        for i, (file_path, file_data) in enumerate(sorted_files[:n_results], 1):
            print(f"\n{i}. {file_path} ({file_data['chunk_count']} chunks)")
            print(f"   Extension: {file_data['extension']}")
            print(f"   Avg distance: {file_data['avg_distance']:.4f}")
            
            # Mostrar chunks más relevantes
            file_data["chunks"].sort(key=lambda x: x["distance"])
            for j, chunk in enumerate(file_data["chunks"][:2], 1):
                print(f"   Chunk {chunk['chunk_index']} (distance {chunk['distance']:.4f}):")
                content = chunk["content"].strip()
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"      {content}")
                
        return sorted_files[:n_results]
        
    def list_files(self):
        """Lista todos los archivos indexados"""
        if not self.collection:
            logger.error("No index loaded")
            return []
            
        # Obtener todos los documentos
        results = self.collection.get(include=["metadatas"])
        
        files = {}
        for metadata in results["metadatas"]:
            file_path = metadata["file_path"]
            if file_path not in files:
                files[file_path] = {
                    "name": metadata["file_name"],
                    "extension": metadata["extension"],
                    "chunks": 0,
                    "size": metadata.get("file_size", 0)
                }
            files[file_path]["chunks"] += 1
            
        return files
        
    def get_stats(self):
        """Obtiene estadísticas del índice"""
        if not self.collection:
            return {}
            
        try:
            stats = self.collection.count()
            files = self.list_files()
            
            return {
                "collection_name": self.collection.name,
                "document_count": stats,
                "file_count": len(files),
                "total_chunks": sum(f["chunks"] for f in files.values()),
                "model_name": self.metadata.get("model_name", "unknown"),
                "indexed_at": self.metadata.get("indexed_at", "unknown"),
                "repo_name": self.metadata.get("repo_name", "unknown")
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

def main():
    parser = argparse.ArgumentParser(description="Universal Continue-style codebase searcher")
    parser.add_argument("repo_path", help="Path to repository with index")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--n-results", type=int, default=10,
                       help="Number of results to show")
    parser.add_argument("--file-filter", help="Filter by file path regex")
    parser.add_argument("--extension", help="Filter by file extension")
    parser.add_argument("--list-files", action="store_true",
                       help="List all indexed files instead of searching")
    parser.add_argument("--stats", action="store_true",
                       help="Show index statistics")
    
    args = parser.parse_args()
    
    # Validar path
    if not os.path.exists(args.repo_path):
        logger.error(f"Repository path does not exist: {args.repo_path}")
        sys.exit(1)
        
    # Crear searcher
    searcher = UniversalContinueSearcher(args.repo_path)
    
    if not searcher.load_index():
        logger.error("Failed to load index")
        sys.exit(1)
        
    if args.stats:
        # Mostrar estadísticas
        stats = searcher.get_stats()
        print(json.dumps(stats, indent=2))
        
    elif args.list_files:
        # Listar archivos
        files = searcher.list_files()
        print(f"\n📁 Indexed files in {args.repo_path}")
        print("=" * 50)
        
        for i, (file_path, file_data) in enumerate(files.items(), 1):
            print(f"{i:3d}. {file_path}")
            print(f"     Extension: {file_data['extension']}")
            print(f"     Chunks: {file_data['chunks']}")
            if file_data['size'] > 0:
                size_mb = file_data['size'] / 1024 / 1024
                print(f"     Size: {size_mb:.2f} MB")
            print()
            
    else:
        # Buscar
        results = searcher.search_files(args.query, args.n_results)
        return len(results)

if __name__ == "__main__":
    main()