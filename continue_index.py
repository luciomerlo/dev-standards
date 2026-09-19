#!/usr/bin/env python3
"""
Universal Continue-style codebase indexer
Indexa un repositorio usando sentence-transformers + ChromaDB
Similar a Continue pero sin VS Code dependencia
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import pathspec
import tiktoken
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import logging

# Configuración logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalContinueIndexer:
    def __init__(self, repo_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.repo_path = Path(repo_path).resolve()
        self.model_name = model_name
        self.model = None
        self.client = None
        self.collection = None
        self.ignore_spec = None
        self.enc = tiktoken.get_encoding("cl100k_base")
        self.indexed_file_path = self.repo_path / ".continue" / "indexed_files.json"
        self.indexed_files = {}
        
    def load_indexed_state(self):
        """Cargar estado previo de archivos indexados"""
        if self.indexed_file_path.exists():
            try:
                with open(self.indexed_file_path, 'r', encoding='utf-8') as f:
                    self.indexed_files = json.load(f)
                logger.info(f"Cargado estado de indexación para {len(self.indexed_files)} archivos")
            except Exception as e:
                logger.warning(f"No se pudo cargar el estado de indexación: {e}")
                self.indexed_files = {}
        else:
            logger.info("No se encontró estado previo de indexación, comenzando desde cero")
            self.indexed_files = {}
    
    def save_indexed_state(self):
        """Guardar estado actual de archivos indexados"""
        try:
            self.indexed_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.indexed_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.indexed_files, f, indent=2)
            logger.debug(f"Estado de indexación guardado para {len(self.indexed_files)} archivos")
        except Exception as e:
            logger.error(f"Error al guardar estado de indexación: {e}")
        
    def load_model(self):
        """Carga el modelo de embeddings"""
        logger.info(f"Cargando modelo: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
    def load_ignore_spec(self):
        """Carga el .gitignore y .continueignore"""
        patterns = []
        
        # .gitignore
        gitignore_path = self.repo_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns.extend(f.readlines())
        
        # .continueignore (prioritario)
        continueignore_path = self.repo_path / ".continueignore"
        if continueignore_path.exists():
            with open(continueignore_path, 'r', encoding='utf-8') as f:
                patterns.extend(f.readlines())
        
        # Patrones por defecto
        default_patterns = [
            "*.log", "*.tmp", "*.temp",
            "node_modules/", "dist/", "build/", "out/",
            "__pycache__/", "*.pyc", ".venv/", "venv/",
            ".git/", ".DS_Store", "Thumbs.db",
            ".vscode/", ".idea/", "*.swp", "*.swo",
            "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*"
        ]
        patterns.extend(default_patterns)
        
        self.ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        logger.info(f"Loaded {len(patterns)} ignore patterns")
        
    def should_ignore(self, file_path: Path) -> bool:
        """Verifica si un archivo debe ser ignorado"""
        rel_path = file_path.relative_to(self.repo_path)
        return self.ignore_spec.match_file(str(rel_path))
        
    def chunk_text(self, text: str, max_tokens: int = 512) -> List[str]:
        """Divide texto en chunks"""
        tokens = self.enc.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.enc.decode(chunk_tokens)
            chunks.append(chunk_text)
            
        return chunks
        
    def index_file(self, file_path: Path):
        """Indexa un archivo individual"""
        try:
            # Verificar extensión
            ext = file_path.suffix.lower()
            supported_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
                '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.m', '.mm',
                '.html', '.css', '.scss', '.sass', '.less',
                '.json', '.yaml', '.yml', '.xml', '.toml', '.ini',
                '.md', '.txt', '.rst', '.doc', '.docx',
                '.sql', '.sh', '.bat', '.ps1', '.dockerfile',
                '.gitignore', '.dockerignore', '.env'
            }
            
            if ext not in supported_extensions:
                return None
                
            # Leer archivo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Generar chunks
            chunks = self.chunk_text(content)
            
            # Preparar documentos para ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Ignorar chunks muy pequeños
                    doc_id = f"{file_path.stem}_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "file_path": str(file_path.relative_to(self.repo_path)),
                        "file_name": file_path.name,
                        "chunk_index": i,
                        "extension": ext,
                        "file_size": len(content),
                        "chunk_size": len(chunk)
                    })
                    ids.append(doc_id)
                    
            # Solo retornar si hay documentos válidos
            if not documents:
                return None
                    
            return {
                "documents": documents,
                "metadatas": metadatas,
                "ids": ids
            }
            
        except Exception as e:
            logger.warning(f"Error indexing {file_path}: {e}")
            return None
            
    def create_collection(self, incremental: bool = False):
        """Crea la colección ChromaDB"""
        # Directorio para el índice
        index_dir = self.repo_path / ".continue" / "index"
        index_dir.mkdir(parents=True, exist_ok=True)
        
        # Cliente ChromaDB persistente
        self.client = chromadb.PersistentClient(path=str(index_dir))
        
        # Nombre de colección basado en el repo
        collection_name = f"{self.repo_path.name}_codebase"
        
        # Función de embeddings
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.model_name
        )
        
        # Crear o obtener colección
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_func,
            metadata={"description": f"Codebase index for {self.repo_path.name}"}
        )
        
        logger.info(f"Collection created: {collection_name}")
        
        # Si es incremental, migrar metadatos existentes (IDs de archivos)
        if incremental and self.collection.count() > 0:
            self._migrate_existing_ids()
    
    def _migrate_existing_ids(self):
        """Migrar IDs de archivos existentes al nuevo esquema"""
        try:
            # Obtener todos los documentos existentes
            existing = self.collection.get(include=[])
            existing_ids = existing.get("ids", [])
            
            # Crear mapa de IDs antiguos a nuevos
            # Los IDs antiguos tienen formato: filename_chunkindex
            # Normalizar para que coincida con el nuevo esquema
            new_ids = []
            for old_id in existing_ids:
                # Intentar extraer nombre de archivo y chunk
                parts = old_id.rsplit("_", 1)
                if len(parts) == 2:
                    filename, chunk_str = parts
                    try:
                        chunk_idx = int(chunk_str)
                        # Mantener en nuevo formato
                        new_ids.append(f"{filename}_{chunk_idx}")
                    except ValueError:
                        new_ids.append(old_id)
                else:
                    new_ids.append(old_id)
            
            # ChromaDB renumbera automáticamente, solo registramos
            logger.info(f"Migrated {len(new_ids)} existing IDs for incremental update")
        except Exception as e:
            logger.warning(f"Error migrating existing IDs: {e}")
        
    def index_repo(self, force_reindex: bool = False, incremental: bool = False):
        """Indexa todo el repositorio"""
        start_time = time.time()
        
        # Cargar modelo y configuración
        self.load_model()
        self.load_ignore_spec()
        self.create_collection()
        
        # Cargar estado previo si es incremental
        if incremental:
            self.load_indexed_state()
        
        # Contadores
        total_files = 0
        indexed_files = 0
        total_chunks = 0
        skipped_files = 0
        updated_files = 0
        new_files = 0
        
        # Recorrer archivos
        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                
                if self.should_ignore(file_path):
                    continue
                
                # Verificar si necesitamos procesar este archivo
                file_mtime = file_path.stat().st_mtime
                file_path_str = str(file_path.relative_to(self.repo_path))
                
                should_process = False
                if force_reindex:
                    should_process = True
                    reason = "force_reindex"
                elif incremental:
                    # En modo incremental, procesar si es nuevo o ha cambiado
                    if file_path_str not in self.indexed_files:
                        should_process = True
                        reason = "nuevo archivo"
                    else:
                        last_mtime = self.indexed_files[file_path_str]
                        if file_mtime > last_mtime:
                            should_process = True
                            reason = "archivo modificado"
                        else:
                            should_process = False
                            reason = "sin cambios"
                else:
                    # No incremental ni force -> siempre procesar (modo completo)
                    should_process = True
                    reason = "modo completo"
                
                if not should_process:
                    skipped_files += 1
                    logger.debug(f"Skipping {file_path_str} ({reason})")
                    continue
                
                logger.info(f"Processing: {file_path_str} ({reason})")
                
                result = self.index_file(file_path)
                if result:
                    # Añadir a ChromaDB
                    self.collection.add(
                        documents=result["documents"],
                        metadatas=result["metadatas"],
                        ids=result["ids"]
                    )
                    
                    indexed_files += 1
                    total_chunks += len(result["documents"])
                    
                    # Actualizar estado de indexación
                    self.indexed_files[file_path_str] = file_mtime
                    
                    if reason == "nuevo archivo":
                        new_files += 1
                    elif reason == "archivo modificado":
                        updated_files += 1
                    # force_reindex cuenta como procesado pero no como nuevo/actualizado específicamente
                else:
                    # Si no se pudo indexar, aún actualizamos el timestamp para no intentar continuamente
                    self.indexed_files[file_path_str] = file_mtime
        
        # Limpiar estado de archivos que ya no existen
        if incremental:
            existing_files = set()
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file() and not self.should_ignore(file_path):
                    existing_files.add(str(file_path.relative_to(self.repo_path)))
            
            to_remove = [k for k in self.indexed_files.keys() if k not in existing_files]
            for k in to_remove:
                del self.indexed_files[k]
                logger.debug(f"Removing deleted file from index state: {k}")
        
        # Guardar metadata del repo
        metadata = {
            "repo_path": str(self.repo_path),
            "repo_name": self.repo_path.name,
            "model_name": self.model_name,
            "indexed_files": indexed_files,
            "total_files": total_files,
            "total_chunks": total_chunks,
            "indexed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "index_version": "1.0"
        }
        
        metadata_path = self.repo_path / ".continue" / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Guardar estado de indexación de archivos
        if incremental:
            self.save_indexed_state()
        
        elapsed = time.time() - start_time
        logger.info(f"Indexing completed in {elapsed:.2f}s")
        logger.info(f"Processed: {indexed_files} files ({new_files} new, {updated_files} updated), {skipped_files} skipped, {total_chunks} total chunks")
        
        return metadata
        
    def search(self, query: str, n_results: int = 10):
        """Busca en el índice"""
        if not self.collection:
            self.create_collection()
        if not self.collection:
            logger.error("No collection loaded. Run index_repo first.")
            return []
            
        # Buscar
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        return results
        
    def get_stats(self):
        """Obtiene estadísticas del índice"""
        if not self.collection:
            return {}
            
        try:
            stats = self.client.get_collection(self.collection.name).count()
            return {
                "collection_name": self.collection.name,
                "document_count": stats,
                "model_name": self.model_name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

def main():
    parser = argparse.ArgumentParser(description="Universal Continue-style codebase indexer")
    parser.add_argument("repo_path", help="Path to repository to index")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", 
                       help="Sentence transformer model name")
    parser.add_argument("--search", help="Search query instead of indexing")
    parser.add_argument("--n-results", type=int, default=10,
                       help="Number of search results")
    parser.add_argument("--stats", action="store_true",
                       help="Show index statistics")
    
    parser.add_argument("--incremental", action="store_true",
                        help="Enable incremental indexing (only new/modified files)")
    parser.add_argument("--force", action="store_true",
                        help="Force re-indexing of all files")

    args = parser.parse_args()
    
    # Validar path
    if not os.path.exists(args.repo_path):
        logger.error(f"Repository path does not exist: {args.repo_path}")
        sys.exit(1)
        
    # Crear indexer
    indexer = UniversalContinueIndexer(args.repo_path, args.model)
    
    if args.search:
        # Buscar
        logger.info(f"Searching for: {args.search}")
        results = indexer.search(args.search, args.n_results)
        
        # Mostrar resultados
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0], 
            results["metadatas"][0], 
            results["distances"][0]
        )):
            print(f"\n{i+1}. {metadata['file_path']} (chunk {metadata['chunk_index']})")
            print(f"   Distance: {distance:.4f}")
            print(f"   Content: {doc[:200]}...")
            
    elif args.stats:
        # Mostrar estadísticas
        stats = indexer.get_stats()
        print(json.dumps(stats, indent=2))
        
    else:
        # Indexar
        logger.info(f"Indexing repository: {args.repo_path}")
        metadata = indexer.index_repo(force_reindex=args.force, incremental=args.incremental)
        print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()