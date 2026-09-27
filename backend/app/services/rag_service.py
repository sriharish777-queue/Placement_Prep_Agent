"""
RAG Career Assistant
- ChromaDB with local sentence-transformer embeddings (free, offline)
- Semantic search over placement knowledge base
- Augmented generation via OpenRouter
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime

from app.core.config import settings
from app.services.llm_client import chat_complete

logger = logging.getLogger(__name__)

_client = None
_collection = None


def _get_ef():
    """Get chromadb local embedding function (sentence-transformers, runs offline)."""
    from chromadb.utils import embedding_functions
    return embedding_functions.DefaultEmbeddingFunction()


def get_chroma_client():
    global _client
    if _client is None:
        import chromadb
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=_get_ef(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


async def add_document(doc_id: str, content: str, metadata: Dict) -> None:
    """Add a document to the RAG knowledge base."""
    try:
        collection = get_collection()
        collection.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata],
        )
        logger.info("Added document %s to RAG store", doc_id)
    except Exception as e:
        logger.error("Failed to add document %s: %s", doc_id, e)
        raise


async def search_knowledge_base(
    query: str,
    n_results: int = 5,
    filter_metadata: Optional[Dict] = None,
) -> List[Dict]:
    """Semantic search — returns top-n relevant documents."""
    try:
        collection = get_collection()
        kwargs = {
            "query_texts": [query],
            "n_results": min(n_results, collection.count() or 1),
            "include": ["documents", "metadatas", "distances"],
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = collection.query(**kwargs)
        docs = []
        for i, doc in enumerate(results["documents"][0]):
            docs.append({
                "content": doc,
                "metadata": results["metadatas"][0][i],
                "relevance_score": round(1 - results["distances"][0][i], 3),
            })
        return docs
    except Exception as e:
        logger.error("RAG search failed: %s", e)
        return []


async def rag_query(
    query: str,
    user_context: Optional[Dict] = None,
    company: Optional[str] = None,
) -> Dict:
    """Full RAG pipeline: retrieve context → generate answer."""

    # Try company filter, fall back to no filter
    filter_meta = {"company": {"$eq": company}} if company else None
    docs = await search_knowledge_base(query, n_results=4, filter_metadata=filter_meta)

    if not docs and company:
        docs = await search_knowledge_base(query, n_results=4)

    context_text = "\n\n".join([
        f"[Source: {d['metadata'].get('source', 'Knowledge Base')} | "
        f"Category: {d['metadata'].get('category', 'General')}]\n{d['content']}"
        for d in docs
    ]) if docs else "No specific context found — answering from general knowledge."

    user_ctx = ""
    if user_context:
        role = user_context.get("target_role", "")
        weak = user_context.get("weak_skills", [])
        if role:
            user_ctx = f"\nStudent is preparing for: {role}"
        if weak:
            user_ctx += f"\nWeak areas to focus on: {', '.join(weak[:5])}"

    system_prompt = """You are an expert placement preparation coach and career advisor.
Use the provided context to give accurate, practical answers.
If the context doesn't fully answer the question, use your general knowledge.
Be specific, give examples, and always be encouraging."""

    user_message = f"""Context from knowledge base:
{context_text}
{user_ctx}

Student question: {query}

Give a comprehensive, practical answer with examples where helpful."""

    try:
        answer = await chat_complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.5,
            max_tokens=1000,
        )
    except Exception as e:
        logger.error("RAG answer generation failed: %s", e)
        answer = (
            "I'm currently unable to generate a detailed answer. "
            "Please check your OpenRouter API connection and try again. "
            f"Your question was: {query}"
        )

    return {
        "answer": answer,
        "sources": [d["metadata"] for d in docs],
        "context_used": len(docs),
    }


async def seed_knowledge_base() -> int:
    """Seed RAG with foundational placement content."""
    seed_docs = [
        {
            "id": "dsa_arrays_001",
            "content": """Arrays — Key Interview Concepts:
1. Two Pointer: sorted array problems, pair sum, palindrome check. O(n) time.
2. Sliding Window: fixed/variable window for subarray problems.
3. Prefix Sum: range query problems in O(1) after O(n) preprocessing.
4. Kadane's Algorithm: max subarray sum in O(n).
5. Binary Search variants: rotated sorted array, peak element, search range.
Common questions: Two Sum, Best Time to Buy/Sell Stock, Maximum Subarray,
Product of Array Except Self, Find Minimum in Rotated Sorted Array.
Time complexity: Access O(1), Search O(n), Insert/Delete O(n).""",
            "metadata": {"category": "DSA", "subcategory": "Arrays", "source": "DSA Fundamentals", "difficulty": "medium"},
        },
        {
            "id": "dsa_dp_001",
            "content": """Dynamic Programming — Interview Guide:
1. Identify overlapping subproblems and optimal substructure.
2. Top-down (memoization) vs Bottom-up (tabulation).
3. Classic patterns: 0/1 Knapsack, LCS, LIS, Coin Change, Edit Distance.
4. State definition is the hardest part — think carefully.
5. Common interview DP: Fibonacci, Climbing Stairs, House Robber, Unique Paths.
Time: O(n^2) or O(n*m) usually. Space: O(n) with space optimization.""",
            "metadata": {"category": "DSA", "subcategory": "Dynamic Programming", "source": "DSA Fundamentals", "difficulty": "hard"},
        },
        {
            "id": "java_oops_001",
            "content": """Java OOP — Interview Essentials:
1. Encapsulation: private fields + public getters/setters. Data hiding.
2. Inheritance: 'extends', IS-A relationship, method overriding (@Override).
3. Polymorphism: compile-time (overloading) vs runtime (overriding).
4. Abstraction: abstract class (can have state) vs Interface (Java 8+ default methods).
5. SOLID: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion.
Key distinctions: abstract class vs interface, overloading vs overriding,
== vs .equals(), String vs StringBuilder.""",
            "metadata": {"category": "Java", "subcategory": "OOP", "source": "Java Interview Guide", "difficulty": "medium"},
        },
        {
            "id": "java_collections_001",
            "content": """Java Collections — Interview Guide:
ArrayList: dynamic array, O(1) get, O(n) insert/delete.
LinkedList: O(1) insert/delete at ends, O(n) get.
HashMap: O(1) avg get/put, not thread-safe. HashTable is thread-safe.
TreeMap: sorted keys, O(log n) operations.
HashSet vs TreeSet: hash-based O(1) vs sorted O(log n).
PriorityQueue: min-heap by default. Use Comparator for max-heap.
ConcurrentHashMap: thread-safe without full synchronization.
Key interview: when to use which collection, internal working of HashMap.""",
            "metadata": {"category": "Java", "subcategory": "Collections", "source": "Java Interview Guide", "difficulty": "medium"},
        },
        {
            "id": "sql_joins_001",
            "content": """SQL Joins — Complete Interview Guide:
INNER JOIN: rows matching in BOTH tables.
LEFT JOIN: all from left + matched from right (NULL if no match).
RIGHT JOIN: all from right + matched from left.
FULL OUTER JOIN: all from both tables.
SELF JOIN: table joined with itself (org hierarchy, employee-manager).
Key patterns:
- Employees without managers: LEFT JOIN WHERE manager_id IS NULL
- Second highest salary: SELECT MAX(salary) WHERE salary < (SELECT MAX(salary)...)
- Nth salary: ROW_NUMBER() OVER (ORDER BY salary DESC)
- Duplicate records: GROUP BY ... HAVING COUNT(*) > 1""",
            "metadata": {"category": "SQL", "subcategory": "Joins", "source": "SQL Interview Prep", "difficulty": "medium"},
        },
        {
            "id": "dbms_normalization_001",
            "content": """DBMS Normalization — Interview Guide:
1NF: Atomic values, no repeating groups, primary key exists.
2NF: 1NF + no partial dependency on composite key.
3NF: 2NF + no transitive dependency (non-key → non-key).
BCNF: For every X→Y, X must be a super key.
ACID: Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions),
Durability (committed = permanent).
Indexing: B-Tree (default, range queries), Hash (exact match), Clustered (one per table),
Non-clustered (multiple allowed). Index speeds SELECT, slows INSERT/UPDATE.""",
            "metadata": {"category": "DBMS", "source": "DBMS Interview Guide", "difficulty": "medium"},
        },
        {
            "id": "os_concepts_001",
            "content": """Operating Systems — Interview Key Concepts:
Process vs Thread: Process = isolated memory space. Thread = shared memory, lightweight.
Deadlock: 4 conditions — Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.
Prevention: break any one condition.
CPU Scheduling: FCFS (simple), SJF (min avg wait), Round Robin (time quantum, fair),
Priority (starvation risk), MLFQ (adaptive).
Virtual Memory: paging, page faults, TLB for fast lookup.
Page Replacement: LRU (optimal in practice), FIFO (simple), Optimal (theoretical best).
Semaphore vs Mutex: Semaphore is a counter (can allow N resources),
Mutex is binary (1 owner at a time).""",
            "metadata": {"category": "OS", "source": "OS Interview Guide", "difficulty": "medium"},
        },
        {
            "id": "cn_concepts_001",
            "content": """Computer Networks — Interview Essentials:
OSI 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application.
TCP vs UDP: TCP = reliable, ordered, connection-based. UDP = fast, no guarantee.
3-way handshake: SYN → SYN-ACK → ACK.
HTTP vs HTTPS: HTTPS uses TLS/SSL for encryption.
DNS: Domain → IP resolution. Recursive vs iterative queries.
Subnetting: CIDR notation, subnet masks, calculating hosts per subnet.
Common ports: HTTP=80, HTTPS=443, SSH=22, FTP=21, DNS=53, MySQL=3306.
REST: stateless, HTTP verbs (GET/POST/PUT/DELETE), JSON responses.""",
            "metadata": {"category": "CN", "source": "CN Interview Guide", "difficulty": "medium"},
        },
        {
            "id": "aptitude_formulas_001",
            "content": """Aptitude Quick Formulas — Placement Tests:
Time & Work: A does in 'a' days, B in 'b' days → together = ab/(a+b) days.
Pipes: filling pipe rate + draining pipe rate = combined rate.
Speed: Speed = Distance/Time. Relative speed same dir = |S1-S2|, opp dir = S1+S2.
Percentage: % change = (new-old)/old × 100.
Profit: Profit% = Profit/CP × 100. SP = CP(1 + P/100).
SI: SI = PRT/100. CI: A = P(1 + R/100)^T.
Permutation: nPr = n!/(n-r)!. Combination: nCr = n!/(r!(n-r)!).
Probability: P = Favourable/Total. P(A∪B) = P(A)+P(B)-P(A∩B).
Series: AP sum = n/2(2a+(n-1)d). GP sum = a(r^n-1)/(r-1).""",
            "metadata": {"category": "Aptitude", "source": "Aptitude Master Guide", "difficulty": "easy"},
        },
        {
            "id": "system_design_001",
            "content": """System Design Interview Framework:
Step 1 — Requirements (5 min): Functional (what it does) + Non-functional (scale, latency).
Step 2 — Capacity Estimation: DAU, requests/sec, storage needed.
Step 3 — High Level Design: Draw components — client, LB, servers, DB, cache.
Step 4 — Database Design: SQL vs NoSQL decision + schema.
Step 5 — Deep Dive: Cache strategy (Redis), CDN, message queues (Kafka).
Step 6 — Bottlenecks: Where will it fail at 10x scale? How to shard?
Popular designs to practice: URL Shortener, Twitter Feed, WhatsApp,
Netflix (streaming), Uber (location tracking), Google Drive (file storage).""",
            "metadata": {"category": "System Design", "source": "System Design Guide", "difficulty": "hard"},
        },
        {
            "id": "behavioral_star_001",
            "content": """Behavioral Interview — STAR Method Guide:
STAR = Situation, Task, Action, Result. Always quantify the Result.

Top questions & approach:
1. "Tell me about yourself" — 2 min: education → key project → skills → goal.
2. "Greatest strength" — Pick technical strength with concrete example.
3. "Greatest weakness" — Real weakness + active improvement steps.
4. "Conflict with teammate" — Show empathy, communication, resolution.
5. "Failure/mistake" — Own it completely, show learning.
6. "Why this company" — Research their tech stack, culture, recent projects.
7. "5-year plan" — Align with company's growth trajectory.
Tips: Be specific not generic. Use numbers. Show ownership and growth mindset.""",
            "metadata": {"category": "Behavioral", "source": "Interview Prep Guide", "difficulty": "easy"},
        },
        {
            "id": "placement_readiness_001",
            "content": """Placement Readiness Checklist:
DSA: LeetCode 150 easy+medium. Focus: arrays, strings, trees, DP, graphs.
CS Fundamentals: OS (processes, deadlocks), DBMS (SQL, normalization), CN (OSI, TCP/IP).
Language: Java/Python — OOP, collections, multithreading basics.
Projects: At least 2 complete projects with GitHub links. Know every line.
Communication: Practice explaining technical concepts simply. Mock interviews weekly.
Aptitude: TCS, Infosys, Wipro pattern — number series, logical reasoning, verbal.
Resume: 1 page, ATS-friendly, quantified achievements, strong action verbs.
Timeline: 3 months for comprehensive prep (DSA daily + 1 CS topic/day + mock weekly).""",
            "metadata": {"category": "General", "source": "Placement Guide", "difficulty": "easy"},
        },
    ]

    count = 0
    for doc in seed_docs:
        try:
            await add_document(
                doc_id=doc["id"],
                content=doc["content"],
                metadata=doc["metadata"],
            )
            count += 1
        except Exception as e:
            logger.error("Failed to seed doc %s: %s", doc["id"], e)

    logger.info("Seeded %d documents into RAG knowledge base", count)
    return count
