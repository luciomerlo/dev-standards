#!/usr/bin/env python3
"""
Multi-repo Continue-style codebase searcher
Busca en los índices de múltiples repositorios
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import glob

# Configuración logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalContinueMultiSearcher:
    def __init__(self, repos_dir: str = "D:\\Projects"):
        self.repos_dir = Path(repos_dir).resolve()
        self.repo_indexes = {}
        
    def scan_for_repos(self, repo_pattern: str = "*"):
        """Escanea directorios para encontrar repositorios con .continue/index"""
        repos = []
        
        # Buscar .continue/index recursivamente
        for index_path in self.repos_dir.rglob(".continue/index"):
            if index_path.is_dir():
                repo_path = index_path.parent.parent  # .continue/index -> repo root
                if repo_path not in repos:
                    repos.append(repo_path)
                    logger.info(f"Found repo index: {repo_path.name}")
                    
        return repos
        
    def load_all_indexes(self, repo_names: List[str] = None):
        """Carga todos los índices de repositorios"""
        repos = self.scan_for_repos()
        
        for repo_path in repos:
            if repo_names and repo_path.name not in repo_names:
                continue
                
            try:
                from continue_search import UniversalContinueSearcher
                searcher = UniversalContinueSearcher(str(repo_path))
                if searcher.load_index():
                    self.repo_indexes[repo_path.name] = {
                        "path": repo_path,
                        "searcher": searcher,
                        "stats": searcher.get_stats()
                    }
                    logger.info(f"Successfully loaded index for {repo_path.name}")
            except Exception as e:
                logger.error(f"Error loading index for {repo_path.name}: {e}")
                
        return len(self.repo_indexes)
        
    def search_all(self, query: str, n_results: int = 5,
                   file_filter: str = None, extension_filter: str = None):
        """Busca en todos los índices de repositorios"""
        if not self.repo_indexes:
            logger.error("No indexes loaded. Run load_all_indexes() first.")
            return []
            
        all_results = {}
        
        for repo_name, repo_data in self.repo_indexes.items():
            logger.info(f"Searching in {repo_name} for: {query}")
            results = repo_data["searcher"].search(query, n_results * 3,
                                                    file_filter, extension_filter)
            all_results[repo_name] = results
            
        return all_results
        
    def search_all_files(self, query: str, n_results: int = 5,
                        file_filter: str = None, extension_filter: str = None):
        """Busca en todos los índices y muestra resultados agrupados por repo"""
        if not self.repo_indexes:
            logger.error("No indexes loaded. Run load_all_indexes() first.")
            return []
            
        all_results = self.search_all(query, n_results * 3, file_filter, extension_filter)
        
        print(f"\n[MULTI-SEARCH] Multi-repo search results for: '{query}'")
        print("=" * 60)
        
        total_results = 0
        for repo_name, results in all_results.items():
            if results and "documents" in results and results["documents"]:
                repo_doc_results = results["documents"][0]
                repo_meta_results = results["metadatas"][0]
                repo_distance_results = results["distances"][0]
                
                # Agrupar por archivo
                files = {}
                for doc, metadata, distance in zip(
                    repo_doc_results, repo_meta_results, repo_distance_results
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
                        file_data["avg_distance"] = sum(
                            c["distance"] for c in file_data["chunks"]
                        ) / len(file_data["chunks"])
                        
                # Ordenar por distancia promedio
                sorted_files = sorted(files.items(), 
                                    key=lambda x: x[1]["avg_distance"])
                
                print(f"\n[REPO] {repo_name.upper()} ({len(sorted_files)} archivos)")
                print("-" * 60)
                
                for i, (file_path, file_data) in enumerate(sorted_files[:n_results], 1):
                    print(f"\n{i}. {file_path} ({file_data['chunk_count']} chunks)")
                    print(f"   Extension: {file_data['extension']}")
                    print(f"   Avg distance: {file_data['avg_distance']:.4f}")
                    
                    # Mostrar chunks más relevantes
                    file_data["chunks"].sort(key=lambda x: x["distance"])
                    for j, chunk in enumerate(file_data["chunks"][:2], 1):
                        print(f"   Chunk {chunk['chunk_index']} (distance {chunk['distance']:.4f}):")
                        content = chunk["content"].strip()
                        # Handle encoding issues
                        content = content.encode('ascii', 'replace').decode('ascii')
                        if len(content) > 200:
                            content = content[:200] + "..."
                        print(f"      {content}")
                        
                total_results += len(sorted_files)
                
        print(f"\n[STATS] Total results across all repos: {total_results}")
        return all_results
        
    def list_all_repos(self):
        """Lista todos los repositorios indexados"""
        if not self.repo_indexes:
            logger.error("No indexes loaded.")
            return []
            
        print(f"\n[REPOS] Indexed repositories:")
        print("=" * 60)
        
        for repo_name, repo_data in self.repo_indexes.items():
            stats = repo_data["stats"]
            print(f"\n{repo_name.upper()}")
            print(f"  Path: {stats['repo_name']}")
            print(f"  Documents: {stats['document_count']}")
            print(f"  Files: {stats['file_count']}")
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"  Model: {stats['model_name']}")
            print(f"  Indexed at: {stats['indexed_at']}")
            
        return list(self.repo_indexes.keys())
        
    def get_all_stats(self):
        """Obtiene estadísticas de todos los índices"""
        if not self.repo_indexes:
            logger.error("No indexes loaded.")
            return {}
            
        all_stats = {}
        for repo_name, repo_data in self.repo_indexes.items():
            all_stats[repo_name] = repo_data["stats"]
            
        return all_stats

def main():
    parser = argparse.ArgumentParser(
        description="Multi-repo Continue-style codebase searcher"
    )
    parser.add_argument("--repos-dir", default="D:\\Projects",
                       help="Directory containing repos with .continue/index")
    parser.add_argument("--repo-names", nargs="+", default=None,
                       help="Specific repo names to load (e.g., gemma-translator LoFiMusicGeneration)")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--n-results", type=int, default=5,
                       help="Number of results per repo")
    parser.add_argument("--file-filter", help="Filter by file path regex")
    parser.add_argument("--extension", help="Filter by file extension")
    parser.add_argument("--list-repos", action="store_true",
                       help="List all indexed repositories")
    parser.add_argument("--stats", action="store_true",
                       help="Show all indexes statistics")
    
    args = parser.parse_args()
    
    # Crear multi searcher
    searcher = UniversalContinueMultiSearcher(args.repos_dir)
    
    # Cargar índices
    repo_names = args.repo_names if args.repo_names else None
    loaded_count = searcher.load_all_indexes(repo_names)
    
    if loaded_count == 0:
        logger.error("No indexes found. Check repos directory and .continue/index folders.")
        sys.exit(1)
        
    if args.stats:
        # Mostrar estadísticas
        stats = searcher.get_all_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        
    elif args.list_repos:
        # Listar repositorios
        searcher.list_all_repos()
        
    elif args.search:
        # Buscar en todos los repos
        searcher.search_all_files(
            args.search, 
            args.n_results, 
            args.file_filter, 
            args.extension
        )
        
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()