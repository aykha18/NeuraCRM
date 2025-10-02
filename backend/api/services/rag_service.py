"""
RAG (Retrieval-Augmented Generation) Service for NeuraCRM
Provides intelligent knowledge base Q&A capabilities with hallucination prevention
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import uuid

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import tiktoken
import PyPDF2
import docx
import re

from api.db import get_db
from api.models import User, Organization
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class DocumentChunk:
    """Represents a chunk of document text with metadata"""
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

class EmbeddedChunk:
    """Represents a document chunk with its vector embedding"""
    def __init__(self, text: str, embedding: List[float], metadata: Dict[str, Any]):
        self.text = text
        self.embedding = embedding
        self.metadata = metadata

class SearchResult:
    """Represents a search result from vector database"""
    def __init__(self, chunk_id: str, score: float, text: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.score = score
        self.text = text
        self.metadata = metadata

class RAGService:
    """Main RAG service for knowledge base Q&A"""

    def __init__(self):
        # Initialize clients
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.pinecone = Pinecone(api_key=self.pinecone_api_key)
        self.openai_client = OpenAI(api_key=self.openai_api_key)

        # Configuration
        self.index_name = "neuracrm-knowledge"
        self.dimension = 1536  # OpenAI text-embedding-ada-002
        self.metric = "cosine"
        self.chunk_size = 1000
        self.chunk_overlap = 200

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Ensure index exists
        self._ensure_index()

    def _ensure_index(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            if self.index_name not in self.pinecone.list_indexes().names():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"Created index: {self.index_name}")
            else:
                logger.info(f"Index {self.index_name} already exists")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise

    async def ingest_document(self, file_path: str, metadata: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Ingest a document into the knowledge base"""
        try:
            logger.info(f"Starting document ingestion: {file_path}")

            # Process document into chunks
            chunks = await self._process_document(file_path, metadata)
            if not chunks:
                return {"status": "error", "message": "No content extracted from document"}

            # Generate embeddings
            embedded_chunks = await self._generate_embeddings(chunks)

            # Store in vector database
            await self._store_embeddings(embedded_chunks)

            # Update metadata with processing info
            metadata.update({
                "chunks_created": len(chunks),
                "embeddings_generated": len(embedded_chunks),
                "processed_at": datetime.utcnow().isoformat(),
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            })

            logger.info(f"Successfully ingested document: {len(embedded_chunks)} chunks")
            return {
                "status": "success",
                "chunks_processed": len(chunks),
                "embeddings_stored": len(embedded_chunks),
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            return {"status": "error", "message": str(e)}

    async def search_knowledge(self, query: str, top_k: int = 5, filters: Dict = None) -> List[SearchResult]:
        """Search the knowledge base for relevant information"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_query_embedding(query)

            # Search vector database
            index = self.pinecone.Index(self.index_name)

            search_request = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True,
                "include_values": False
            }

            if filters:
                search_request["filter"] = filters

            results = index.query(**search_request)

            # Format results
            search_results = []
            for match in results['matches']:
                search_results.append(SearchResult(
                    chunk_id=match['id'],
                    score=match['score'],
                    text=match['metadata']['text'],
                    metadata={k: v for k, v in match['metadata'].items() if k != 'text'}
                ))

            return search_results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    async def generate_answer(self, query: str, context_chunks: List[SearchResult],
                            customer_context: Dict = None) -> Dict[str, Any]:
        """Generate an answer using RAG with retrieved context"""
        try:
            # Build context from retrieved chunks
            context = self._build_context(context_chunks, customer_context)

            # Construct RAG prompt
            prompt = self._build_rag_prompt(query, context)

            # Generate response
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful customer support assistant. Use only the provided context to answer questions accurately. If you cannot find the answer in the context, say so clearly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=1000
            )

            answer = response.choices[0].message.content

            # Extract citations
            citations = self._extract_citations(context_chunks, answer)

            return {
                "answer": answer,
                "citations": citations,
                "sources_used": len(context_chunks),
                "confidence_score": self._calculate_confidence(context_chunks),
                "query": query
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I apologize, but I'm unable to provide an answer at this time. Please try rephrasing your question or contact our support team.",
                "citations": [],
                "sources_used": 0,
                "confidence_score": 0.0,
                "error": str(e)
            }

    async def _process_document(self, file_path: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Process a document file into chunks"""
        try:
            file_path = Path(file_path)

            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text = self._extract_pdf_text(str(file_path))
            elif file_path.suffix.lower() == '.docx':
                text = self._extract_docx_text(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")

            # Clean and preprocess text
            cleaned_text = self._clean_text(text)

            # Split into chunks
            chunks = self.text_splitter.split_text(cleaned_text)

            # Create DocumentChunk objects with metadata
            document_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **metadata,
                    'chunk_id': f"{metadata.get('document_id', 'unknown')}_chunk_{i}",
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'word_count': len(chunk.split()),
                    'created_at': datetime.utcnow().isoformat()
                }
                document_chunks.append(DocumentChunk(text=chunk, metadata=chunk_metadata))

            return document_chunks

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return []

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove excessive whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text.strip()

    async def _generate_embeddings(self, chunks: List[DocumentChunk]) -> List[EmbeddedChunk]:
        """Generate embeddings for document chunks"""
        embedded_chunks = []

        # Process in batches to avoid rate limits
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk.text for chunk in batch]

            try:
                # Generate embeddings using OpenAI
                response = await self.openai_client.embeddings.create(
                    input=texts,
                    model="text-embedding-ada-002"
                )

                embeddings = [data.embedding for data in response.data]

                # Create embedded chunks
                for chunk, embedding in zip(batch, embeddings):
                    embedded_chunks.append(EmbeddedChunk(
                        text=chunk.text,
                        embedding=embedding,
                        metadata=chunk.metadata
                    ))

            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {e}")
                continue

        return embedded_chunks

    async def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        try:
            response = await self.openai_client.embeddings.create(
                input=[query],
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    async def _store_embeddings(self, embedded_chunks: List[EmbeddedChunk]):
        """Store embeddings in Pinecone vector database"""
        try:
            index = self.pinecone.Index(self.index_name)

            vectors = []
            for chunk in embedded_chunks:
                vector_data = {
                    'id': chunk.metadata['chunk_id'],
                    'values': chunk.embedding,
                    'metadata': {
                        'text': chunk.text,
                        **{k: v for k, v in chunk.metadata.items() if k != 'chunk_id'}
                    }
                }
                vectors.append(vector_data)

            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)

            logger.info(f"Stored {len(vectors)} embeddings in vector database")

        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            raise

    def _build_context(self, chunks: List[SearchResult], customer_context: Dict = None) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []

        # Sort by relevance score
        sorted_chunks = sorted(chunks, key=lambda x: x.score, reverse=True)

        for chunk in sorted_chunks[:5]:  # Limit to top 5 chunks
            chunk_text = f"""
[Source: {chunk.metadata.get('document_title', 'Unknown')} - Relevance: {chunk.score:.3f}]
{chunk.text}

"""
            context_parts.append(chunk_text)

        # Add customer context if available
        if customer_context:
            customer_info = f"""
Customer Context:
- Account: {customer_context.get('account_type', 'N/A')}
- Support History: {customer_context.get('ticket_count', 0)} tickets
- Plan: {customer_context.get('plan', 'N/A')}

"""
            context_parts.insert(0, customer_info)

        return "\n".join(context_parts)

    def _build_rag_prompt(self, query: str, context: str) -> str:
        """Build the RAG prompt for LLM generation"""
        return f"""
Based on the following context from our knowledge base, please answer the customer's question.

Context:
{context}

Customer Question: {query}

Instructions:
1. Answer based ONLY on the provided context
2. If the context doesn't contain the answer, say "I don't have that information in our knowledge base"
3. Be helpful and professional
4. Include specific references to source documents when relevant
5. Keep the response concise but comprehensive

Answer:"""

    def _extract_citations(self, chunks: List[SearchResult], answer: str) -> List[Dict[str, Any]]:
        """Extract citations from the answer"""
        citations = []
        for chunk in chunks:
            if chunk.text.lower() in answer.lower():
                citations.append({
                    "document_title": chunk.metadata.get('document_title', 'Unknown'),
                    "document_type": chunk.metadata.get('type', 'Unknown'),
                    "relevance_score": chunk.score,
                    "chunk_id": chunk.chunk_id
                })
        return citations

    def _calculate_confidence(self, chunks: List[SearchResult]) -> float:
        """Calculate confidence score based on retrieval results"""
        if not chunks:
            return 0.0

        # Average relevance score with diminishing returns
        avg_score = sum(chunk.score for chunk in chunks) / len(chunks)

        # Boost confidence if we have multiple relevant results
        confidence_boost = min(len(chunks) * 0.1, 0.3)

        return min(avg_score + confidence_boost, 1.0)

# Global RAG service instance
rag_service = RAGService()