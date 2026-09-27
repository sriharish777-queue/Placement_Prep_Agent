"""
Preparation Plan Generator
- Creates 7/14/30-day structured preparation plans
- Based on skill gap analysis output & target role/company
- Combines AI intelligence with a bulletproof, role-specific curriculum engine
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.llm_client import chat_complete_json
from app.models.preparation_plan import PreparationPlan, DayPlan, DailyTask
from app.core.database import get_plans_collection, get_database
from bson import ObjectId

logger = logging.getLogger(__name__)

# ── 30-Day Curated Syllabus: Data Analyst / Business Intelligence / Analytics ──
DATA_ANALYST_SYLLABUS = [
    # Phase 1: Core SQL Mastery (Days 1–8)
    {"focus": ["SQL", "Aptitude"], "tasks": [
        {"topic": "SQL", "subtopic": "SELECT, WHERE, LIKE, ORDER BY, GROUP BY & HAVING", "mins": 90, "diff": "easy", "q": 8, "res": ["HackerRank Basic SQL", "W3Schools SQL Tutorial"]},
        {"topic": "Aptitude", "subtopic": "Percentages, Profit & Loss, Ratios & Averages", "mins": 45, "diff": "easy", "q": 5, "res": ["IndiaBIX Quantitative Aptitude"]},
    ]},
    {"focus": ["SQL", "DBMS"], "tasks": [
        {"topic": "SQL", "subtopic": "Multi-Table Joins: INNER, LEFT, RIGHT, FULL OUTER & CROSS", "mins": 90, "diff": "easy", "q": 6, "res": ["LeetCode 175: Combine Two Tables", "SQLBolt Joins Guide"]},
        {"topic": "DBMS", "subtopic": "Primary Keys, Foreign Keys, Unique Constraints & Clustered Indexes", "mins": 45, "diff": "easy", "q": 4, "res": ["GeeksforGeeks DBMS Indexing"]},
    ]},
    {"focus": ["SQL", "Communication"], "tasks": [
        {"topic": "SQL", "subtopic": "Subqueries, Correlated Subqueries & Common Table Expressions (WITH CTE)", "mins": 100, "diff": "medium", "q": 6, "res": ["Mode Analytics Subqueries & CTEs", "LeetCode 184: Dept Highest Salary"]},
        {"topic": "Communication", "subtopic": "Explaining Query Logic & Data Findings to Non-Technical Stakeholders", "mins": 35, "diff": "easy", "q": 2, "res": ["STAR Method for Analytical Explanations"]},
    ]},
    {"focus": ["SQL", "Aptitude"], "tasks": [
        {"topic": "SQL", "subtopic": "Window Functions: ROW_NUMBER, RANK, DENSE_RANK & NTILE", "mins": 100, "diff": "medium", "q": 6, "res": ["StrataScratch Window Functions", "LeetCode 178: Rank Scores"]},
        {"topic": "Aptitude", "subtopic": "Data Interpretation: Tables, Bar Graphs & Pie Charts", "mins": 45, "diff": "easy", "q": 5, "res": ["IndiaBIX Data Interpretation"]},
    ]},
    {"focus": ["SQL", "DBMS"], "tasks": [
        {"topic": "SQL", "subtopic": "Advanced Window Functions: LEAD, LAG, Running Totals & Moving Averages", "mins": 100, "diff": "medium", "q": 5, "res": ["LeetCode 180: Consecutive Numbers", "PostgreSQL Window Functions Guide"]},
        {"topic": "DBMS", "subtopic": "Database Normalization (1NF, 2NF, 3NF, BCNF) & Denormalization", "mins": 45, "diff": "medium", "q": 4, "res": ["Gate Smashers Normalization Lecture"]},
    ]},
    {"focus": ["SQL", "Aptitude"], "tasks": [
        {"topic": "SQL", "subtopic": "Date/Time Manipulation & String Parsing (EXTRACT, DATEDIFF, CONCAT, COALESCE)", "mins": 90, "diff": "medium", "q": 6, "res": ["LeetCode 197: Rising Temperature", "SQL Date Functions Guide"]},
        {"topic": "Aptitude", "subtopic": "Permutation & Combination, Probability Basics", "mins": 45, "diff": "medium", "q": 5, "res": ["IndiaBIX Probability Practice"]},
    ]},
    {"focus": ["SQL", "Behavioral"], "tasks": [
        {"topic": "SQL", "subtopic": "Amazon-style SQL Interview: Top Customers, Churn & Retention Analysis", "mins": 100, "diff": "hard", "q": 4, "res": ["StrataScratch Amazon SQL Interview Problems"]},
        {"topic": "Behavioral", "subtopic": "Amazon Leadership Principle: Customer Obsession with Data Evidence", "mins": 40, "diff": "medium", "q": 3, "res": ["Amazon Leadership Principles Guide"]},
    ]},
    {"focus": ["SQL", "Aptitude"], "tasks": [
        {"topic": "SQL", "subtopic": "Query Optimization: EXPLAIN PLAN, Query Cost, Indexing Strategies", "mins": 90, "diff": "hard", "q": 4, "res": ["Use The Index, Luke! SQL Performance"]},
        {"topic": "Aptitude", "subtopic": "Speed Calculation & Mental Math for Analytical Interviews", "mins": 40, "diff": "easy", "q": 5, "res": ["Vedic Math Speed Techniques"]},
    ]},

    # Phase 2: Excel & BI Dashboards — Power BI & Tableau (Days 9–14)
    {"focus": ["Excel"], "tasks": [
        {"topic": "Excel", "subtopic": "Advanced Formulas: XLOOKUP, INDEX-MATCH, SUMIFS, COUNTIFS, Dynamic Arrays", "mins": 90, "diff": "easy", "q": 6, "res": ["ExcelJet Advanced Lookup Guide", "Chandoo Excel Formulas"]},
        {"topic": "Excel", "subtopic": "Conditional Formatting, Data Validation & Scenario Manager", "mins": 45, "diff": "easy", "q": 4, "res": ["Microsoft Excel Training Center"]},
    ]},
    {"focus": ["Excel"], "tasks": [
        {"topic": "Excel", "subtopic": "Pivot Tables, Slicers, Timelines & Calculated Fields", "mins": 90, "diff": "medium", "q": 5, "res": ["Leila Gharani Pivot Table Masterclass"]},
        {"topic": "Excel", "subtopic": "Power Query for Data Ingestion, Cleaning & Transformation", "mins": 50, "diff": "medium", "q": 3, "res": ["Power Query M Basics Guide"]},
    ]},
    {"focus": ["Power BI", "DBMS"], "tasks": [
        {"topic": "Power BI", "subtopic": "Data Modeling: Star Schema vs Snowflake, Fact & Dimension Tables, Cardinality", "mins": 90, "diff": "medium", "q": 4, "res": ["Microsoft Learn: Design a Data Model in Power BI"]},
        {"topic": "DBMS", "subtopic": "OLAP vs OLTP & Dimensional Modeling Techniques", "mins": 45, "diff": "medium", "q": 3, "res": ["Kimball Dimensional Modeling Techniques"]},
    ]},
    {"focus": ["Power BI", "Aptitude"], "tasks": [
        {"topic": "Power BI", "subtopic": "DAX Foundations: CALCULATE, FILTER, ALL, ALLEXCEPT, RELATED, SUMX", "mins": 100, "diff": "medium", "q": 5, "res": ["SQLBI: Introducing CALCULATE", "DAX Guide"]},
        {"topic": "Aptitude", "subtopic": "Logical Reasoning: Syllogisms, Seating Arrangement & Blood Relations", "mins": 40, "diff": "medium", "q": 5, "res": ["IndiaBIX Logical Reasoning"]},
    ]},
    {"focus": ["Power BI", "Tableau"], "tasks": [
        {"topic": "Power BI", "subtopic": "DAX Time Intelligence: YTD, QTD, MoM & YoY Growth Measures", "mins": 90, "diff": "hard", "q": 4, "res": ["SQLBI Time Intelligence in DAX"]},
        {"topic": "Tableau", "subtopic": "Data Visualization Best Practices: Visual Hierarchy, KPI Cards, Drill-throughs", "mins": 45, "diff": "easy", "q": 3, "res": ["Storytelling with Data by Cole Nussbaumer"]},
    ]},
    {"focus": ["Power BI", "Communication"], "tasks": [
        {"topic": "Power BI", "subtopic": "Executive Sales & Operations Dashboard: Interactive Bookmarks & Tooltips", "mins": 100, "diff": "hard", "q": 3, "res": ["Maven Analytics Dashboard Challenges"]},
        {"topic": "Communication", "subtopic": "Delivering an Executive Presentation of Dashboard Insights to Leadership", "mins": 40, "diff": "medium", "q": 2, "res": ["McKinsey Pyramid Principle for Business Presentations"]},
    ]},

    # Phase 3: Python for Data Analysis & Statistics (Days 15–21)
    {"focus": ["Python", "Aptitude"], "tasks": [
        {"topic": "Python", "subtopic": "NumPy & Pandas Foundations: Series, DataFrames, Slicing & Data Types", "mins": 90, "diff": "easy", "q": 6, "res": ["10 Minutes to Pandas", "Kaggle Pandas Course"]},
        {"topic": "Aptitude", "subtopic": "Time & Work, Pipes & Cisterns", "mins": 45, "diff": "easy", "q": 5, "res": ["IndiaBIX Time & Work"]},
    ]},
    {"focus": ["Python"], "tasks": [
        {"topic": "Python", "subtopic": "Data Cleaning in Pandas: fillna, dropna, regex replace, str methods & deduplication", "mins": 90, "diff": "medium", "q": 6, "res": ["Real Python: Data Cleaning with Pandas"]},
        {"topic": "Python", "subtopic": "Lambda functions, map, apply, and vectorized operations", "mins": 45, "diff": "medium", "q": 4, "res": ["Pandas Apply vs Vectorization Guide"]},
    ]},
    {"focus": ["Python", "Aptitude"], "tasks": [
        {"topic": "Python", "subtopic": "Grouping, Aggregating, Merging, Joining & Reshaping (pivot_table, melt)", "mins": 90, "diff": "medium", "q": 5, "res": ["LeetCode Pandas 30 Days Challenge"]},
        {"topic": "Aptitude", "subtopic": "Time, Speed & Distance, Trains & Boats", "mins": 45, "diff": "medium", "q": 5, "res": ["IndiaBIX Speed & Distance"]},
    ]},
    {"focus": ["Python", "Statistics"], "tasks": [
        {"topic": "Python", "subtopic": "Exploratory Data Analysis (EDA) with Matplotlib & Seaborn (Histograms, Heatmaps, Boxplots)", "mins": 90, "diff": "medium", "q": 4, "res": ["Kaggle Data Visualization Micro-Course"]},
        {"topic": "Statistics", "subtopic": "Descriptive Statistics: Mean, Median, Mode, Variance, IQR & Outlier Detection", "mins": 50, "diff": "medium", "q": 4, "res": ["StatQuest: Descriptive Statistics"]},
    ]},
    {"focus": ["Statistics", "Aptitude"], "tasks": [
        {"topic": "Statistics", "subtopic": "Probability Distributions: Normal, Binomial, Poisson & Central Limit Theorem", "mins": 90, "diff": "medium", "q": 4, "res": ["StatQuest: The Normal Distribution & CLT"]},
        {"topic": "Aptitude", "subtopic": "Simple & Compound Interest, Profit Margins", "mins": 40, "diff": "easy", "q": 5, "res": ["IndiaBIX Interest Problems"]},
    ]},
    {"focus": ["Statistics", "Behavioral"], "tasks": [
        {"topic": "Statistics", "subtopic": "Hypothesis Testing: Null Hypothesis, p-value, Z-test, T-test & Confidence Intervals", "mins": 90, "diff": "hard", "q": 4, "res": ["Khan Academy: Hypothesis Testing"]},
        {"topic": "Behavioral", "subtopic": "Amazon Leadership Principle: Dive Deep & Bias for Action", "mins": 45, "diff": "medium", "q": 3, "res": ["Amazon Dive Deep Case Studies"]},
    ]},
    {"focus": ["A/B Testing", "SQL"], "tasks": [
        {"topic": "A/B Testing", "subtopic": "A/B Testing Framework: Sample Size, Significance, Minimum Detectable Effect & Pitfalls", "mins": 90, "diff": "hard", "q": 4, "res": ["Exp-Platform A/B Testing Guide", "Evan Miller A/B Sample Size Calculator"]},
        {"topic": "SQL", "subtopic": "SQL Experimentation Queries: Calculating Conversion Rates & Significance in SQL", "mins": 50, "diff": "hard", "q": 3, "res": ["Mode Analytics SQL A/B Testing"]},
    ]},

    # Phase 4: Business Metrics, Case Studies & Amazon Culture (Days 22–27)
    {"focus": ["Business Metrics", "Aptitude"], "tasks": [
        {"topic": "Business Metrics", "subtopic": "E-Commerce & SaaS Metrics: GMV, CAC, LTV, Retention, Churn, NPS & Basket Size", "mins": 90, "diff": "medium", "q": 5, "res": ["Reforge Product Metrics Encyclopedia"]},
        {"topic": "Aptitude", "subtopic": "Critical Reasoning, Statement & Assumptions", "mins": 45, "diff": "medium", "q": 5, "res": ["IndiaBIX Statement & Assumptions"]},
    ]},
    {"focus": ["Case Study", "Communication"], "tasks": [
        {"topic": "Case Study", "subtopic": "Root Cause Analysis (RCA): Investigating a 15% drop in Amazon Cart Checkout Conversion", "mins": 100, "diff": "hard", "q": 3, "res": ["Exponent Product Sense & Metric RCA Frameworks"]},
        {"topic": "Communication", "subtopic": "Writing a 1-page RCA memo for Senior Leadership", "mins": 40, "diff": "medium", "q": 2, "res": ["Amazon 6-Pager / 1-Pager Writing Style Guide"]},
    ]},
    {"focus": ["System Design", "Behavioral"], "tasks": [
        {"topic": "System Design", "subtopic": "Cloud Data Platforms: AWS Redshift, S3 Data Lake, ETL vs ELT pipelines", "mins": 90, "diff": "medium", "q": 4, "res": ["AWS Data Analytics Fundamentals"]},
        {"topic": "Behavioral", "subtopic": "Amazon Leadership Principle: Deliver Results & Invent and Simplify", "mins": 45, "diff": "medium", "q": 3, "res": ["Amazon Leadership Questions STAR Prep"]},
    ]},
    {"focus": ["Behavioral", "Communication"], "tasks": [
        {"topic": "Behavioral", "subtopic": "STAR Method Masterclass: Drafting 5 High-Impact Stories from Past Projects & Internships", "mins": 90, "diff": "medium", "q": 5, "res": ["Dan Croitor Amazon Behavioral Interview Videos"]},
        {"topic": "Communication", "subtopic": "Handling Ambiguity & Disagree and Commit Scenarios", "mins": 40, "diff": "medium", "q": 2, "res": ["Amazon Bar Raiser Interview Tips"]},
    ]},
    {"focus": ["Case Study", "SQL"], "tasks": [
        {"topic": "Case Study", "subtopic": "Amazon Prime Video / E-commerce User Engagement & Cohort Analysis", "mins": 90, "diff": "hard", "q": 3, "res": ["Cohort Retention Analysis Guide"]},
        {"topic": "SQL", "subtopic": "Writing Self-Contained Cohort Retention SQL queries", "mins": 50, "diff": "hard", "q": 3, "res": ["StrataScratch Advanced SQL"]},
    ]},
    {"focus": ["Python", "Aptitude"], "tasks": [
        {"topic": "Python", "subtopic": "Applied ML Basics for Analysts: Linear Regression, Logistic Regression & Scikit-learn", "mins": 90, "diff": "medium", "q": 4, "res": ["StatQuest: Machine Learning in Python"]},
        {"topic": "Aptitude", "subtopic": "Full-Length Aptitude Practice Test (30 questions under time limit)", "mins": 50, "diff": "hard", "q": 30, "res": ["IndiaBIX Mock Test"]},
    ]},

    # Phase 5: Mock Interviews & Final Readiness (Days 28–30)
    {"focus": ["Mock Interview", "Behavioral"], "tasks": [
        {"topic": "Mock Interview", "subtopic": "Full Technical Interview 1: 45-min live SQL coding + 15-min metric evaluation", "mins": 90, "diff": "hard", "q": 4, "res": ["PrepCopilot Mock Interview Module"]},
        {"topic": "Behavioral", "subtopic": "Amazon Bar Raiser Mock Session: Leadership Principles Deep Dive", "mins": 50, "diff": "hard", "q": 4, "res": ["PrepCopilot Behavioral Mock"]},
    ]},
    {"focus": ["Mock Interview", "Communication"], "tasks": [
        {"topic": "Mock Interview", "subtopic": "Full Technical Interview 2: Business Case Study + Python Analysis + Dashboard walkthrough", "mins": 90, "diff": "hard", "q": 3, "res": ["PrepCopilot Mock Interview Module"]},
        {"topic": "Communication", "subtopic": "Interview Q&A: Asking Insightful Questions to the Interviewer", "mins": 40, "diff": "easy", "q": 3, "res": ["Questions to ask your Amazon Interviewer"]},
    ]},
    {"focus": ["Revision"], "tasks": [
        {"topic": "Revision", "subtopic": "Cheat Sheet Review: SQL Window Functions, DAX, Python methods & Business Formulas", "mins": 90, "diff": "easy", "q": 10, "res": ["Placement Prep Ultimate Cheatsheet"]},
        {"topic": "Revision", "subtopic": "Resume Project Walkthrough & Final Confidence Strategy", "mins": 50, "diff": "easy", "q": 2, "res": ["Final Placement Day Checklist"]},
    ]},
]

# ── 30-Day Curated Syllabus: Software Engineer / SDE / Full Stack / Backend ──
SDE_SYLLABUS = [
    # Phase 1: Foundations & Arrays (Days 1–5)
    {"focus": ["DSA", "Aptitude"], "tasks": [
        {"topic": "DSA", "subtopic": "Arrays & Strings: Two Pointers, Sliding Window, Prefix Sum", "mins": 90, "diff": "easy", "q": 6, "res": ["LeetCode 75", "Striver A2Z Sheet"]},
        {"topic": "Aptitude", "subtopic": "Percentages, Profit & Loss, Number Systems", "mins": 45, "diff": "easy", "q": 5, "res": ["IndiaBIX Aptitude"]},
    ]},
    {"focus": ["DSA", "OOP"], "tasks": [
        {"topic": "DSA", "subtopic": "Hashing, Frequency Maps & Two Sum Variations", "mins": 90, "diff": "easy", "q": 6, "res": ["LeetCode Top Interview 150"]},
        {"topic": "OOP", "subtopic": "Encapsulation, Inheritance, Polymorphism & Abstraction with Code", "mins": 45, "diff": "easy", "q": 4, "res": ["OOP Concepts Guide"]},
    ]},
    {"focus": ["DSA", "DBMS"], "tasks": [
        {"topic": "DSA", "subtopic": "Linked Lists: Reverse, Detect Cycle, Merge K Sorted Lists", "mins": 90, "diff": "medium", "q": 5, "res": ["LeetCode Linked List Guide"]},
        {"topic": "DBMS", "subtopic": "SQL Joins, Aggregations, Subqueries & Indexes", "mins": 45, "diff": "easy", "q": 5, "res": ["SQL Tutorial"]},
    ]},
    {"focus": ["DSA", "OS"], "tasks": [
        {"topic": "DSA", "subtopic": "Stacks & Queues: Next Greater Element, Valid Parentheses, Monotonic Stack", "mins": 90, "diff": "medium", "q": 5, "res": ["LeetCode Stacks"]},
        {"topic": "OS", "subtopic": "Processes vs Threads, Concurrency & CPU Scheduling Algorithms", "mins": 45, "diff": "medium", "q": 4, "res": ["Gate Smashers OS"]},
    ]},
    {"focus": ["DSA", "CN"], "tasks": [
        {"topic": "DSA", "subtopic": "Binary Search: Rotated Array, Search in 2D Matrix, Peak Element", "mins": 90, "diff": "medium", "q": 5, "res": ["Binary Search Masterclass"]},
        {"topic": "CN", "subtopic": "OSI Model, TCP/IP, TCP vs UDP 3-Way Handshake", "mins": 45, "diff": "easy", "q": 4, "res": ["Computer Networks Guide"]},
    ]},

    # Phase 2: Trees, Graphs & Core CS (Days 6–15)
    {"focus": ["DSA", "DBMS"], "tasks": [
        {"topic": "DSA", "subtopic": "Binary Trees: Traversals (Inorder, Preorder, Postorder, Level Order)", "mins": 90, "diff": "medium", "q": 5, "res": ["Tree Traversals Guide"]},
        {"topic": "DBMS", "subtopic": "ACID Properties, Transactions & Concurrency Control", "mins": 45, "diff": "medium", "q": 4, "res": ["DBMS Transactions"]},
    ]},
    {"focus": ["DSA", "OS"], "tasks": [
        {"topic": "DSA", "subtopic": "Binary Search Trees (BST): Validation, LCA, Kth Smallest Element", "mins": 90, "diff": "medium", "q": 5, "res": ["LeetCode BST"]},
        {"topic": "OS", "subtopic": "Process Synchronization: Mutex, Semaphore, Deadlock Handling", "mins": 45, "diff": "medium", "q": 4, "res": ["Deadlock Conditions"]},
    ]},
    {"focus": ["DSA", "Aptitude"], "tasks": [
        {"topic": "DSA", "subtopic": "Heaps & Priority Queues: Top K Frequent Elements, Find Median from Stream", "mins": 90, "diff": "medium", "q": 5, "res": ["Heap Patterns"]},
        {"topic": "Aptitude", "subtopic": "Time & Work, Speed & Distance", "mins": 45, "diff": "medium", "q": 5, "res": ["IndiaBIX"]},
    ]},
    {"focus": ["DSA", "CN"], "tasks": [
        {"topic": "DSA", "subtopic": "Graph BFS & DFS: Number of Islands, Clone Graph", "mins": 90, "diff": "medium", "q": 5, "res": ["Graph Traversal Sheet"]},
        {"topic": "CN", "subtopic": "DNS, HTTP/HTTPS, SSL/TLS Handshake & Web Sockets", "mins": 45, "diff": "medium", "q": 4, "res": ["How the Web Works"]},
    ]},
    {"focus": ["DSA", "OOP"], "tasks": [
        {"topic": "DSA", "subtopic": "Graph Algorithms: Topological Sort, Cycle Detection (Kahn's / DFS)", "mins": 90, "diff": "hard", "q": 4, "res": ["Topological Sort Guide"]},
        {"topic": "OOP", "subtopic": "SOLID Principles with Real-World Code Examples", "mins": 45, "diff": "medium", "q": 4, "res": ["SOLID Explained"]},
    ]},
    {"focus": ["DSA", "System Design"], "tasks": [
        {"topic": "DSA", "subtopic": "Shortest Path: Dijkstra, Bellman-Ford & Minimum Spanning Tree", "mins": 90, "diff": "hard", "q": 4, "res": ["Dijkstra Guide"]},
        {"topic": "System Design", "subtopic": "Client-Server Architecture, Monolith vs Microservices", "mins": 45, "diff": "easy", "q": 3, "res": ["System Design Primer"]},
    ]},
    {"focus": ["DSA", "OS"], "tasks": [
        {"topic": "DSA", "subtopic": "Recursion & Backtracking: Subsets, Permutations, N-Queens", "mins": 90, "diff": "medium", "q": 5, "res": ["Backtracking Template"]},
        {"topic": "OS", "subtopic": "Virtual Memory, Paging, Page Replacement (LRU, FIFO)", "mins": 45, "diff": "medium", "q": 4, "res": ["Memory Management"]},
    ]},
    {"focus": ["DSA", "DBMS"], "tasks": [
        {"topic": "DSA", "subtopic": "Dynamic Programming I: 1D DP (Climbing Stairs, House Robber, Coin Change)", "mins": 100, "diff": "medium", "q": 5, "res": ["DP Patterns"]},
        {"topic": "DBMS", "subtopic": "SQL Window Functions: ROW_NUMBER, RANK, DENSE_RANK", "mins": 40, "diff": "medium", "q": 4, "res": ["SQL Window Functions"]},
    ]},
    {"focus": ["DSA", "System Design"], "tasks": [
        {"topic": "DSA", "subtopic": "Dynamic Programming II: 2D DP (Longest Common Subsequence, 0/1 Knapsack)", "mins": 100, "diff": "hard", "q": 4, "res": ["2D DP Guide"]},
        {"topic": "System Design", "subtopic": "Database Sharding, Replication & CAP Theorem", "mins": 45, "diff": "medium", "q": 3, "res": ["CAP Theorem Primer"]},
    ]},
    {"focus": ["DSA", "Aptitude"], "tasks": [
        {"topic": "DSA", "subtopic": "Dynamic Programming III: Stock Buy/Sell, Longest Increasing Subsequence", "mins": 100, "diff": "hard", "q": 4, "res": ["DP on Subsequences"]},
        {"topic": "Aptitude", "subtopic": "Permutation & Combination, Probability", "mins": 40, "diff": "medium", "q": 5, "res": ["IndiaBIX Probability"]},
    ]},

    # Phase 3: System Design, Advanced Coding & Company Prep (Days 16–25)
    {"focus": ["DSA", "System Design"], "tasks": [
        {"topic": "DSA", "subtopic": "Trie Data Structure: Implement Trie, Word Search II", "mins": 90, "diff": "hard", "q": 4, "res": ["Trie Implementation"]},
        {"topic": "System Design", "subtopic": "Caching Strategies (Redis, Memcached, Cache-Aside, Write-Through)", "mins": 50, "diff": "medium", "q": 3, "res": ["System Design Primer Caching"]},
    ]},
    {"focus": ["System Design", "OOP"], "tasks": [
        {"topic": "System Design", "subtopic": "Design a URL Shortener (TinyURL): APIs, Schema & Hashing", "mins": 90, "diff": "medium", "q": 3, "res": ["TinyURL Design Guide"]},
        {"topic": "OOP", "subtopic": "Design Patterns: Factory, Singleton, Strategy & Observer Pattern", "mins": 50, "diff": "medium", "q": 4, "res": ["Refactoring Guru Patterns"]},
    ]},
    {"focus": ["DSA", "System Design"], "tasks": [
        {"topic": "DSA", "subtopic": "Disjoint Set Union (Union Find): Redundant Connection, Kruskal's", "mins": 90, "diff": "hard", "q": 4, "res": ["DSU Patterns"]},
        {"topic": "System Design", "subtopic": "Load Balancing Algorithms & Reverse Proxies (Nginx)", "mins": 45, "diff": "medium", "q": 3, "res": ["Load Balancers Guide"]},
    ]},
    {"focus": ["System Design", "Behavioral"], "tasks": [
        {"topic": "System Design", "subtopic": "Design Rate Limiter (Token Bucket, Leaky Bucket Algorithms)", "mins": 90, "diff": "hard", "q": 3, "res": ["Alex Xu System Design"]},
        {"topic": "Behavioral", "subtopic": "STAR Method: Preparing stories for Conflict, Failure & Innovation", "mins": 45, "diff": "medium", "q": 3, "res": ["Behavioral Question Prep"]},
    ]},
    {"focus": ["DSA", "REST API"], "tasks": [
        {"topic": "DSA", "subtopic": "Bit Manipulation: Single Number, Counting Bits, Power of Two", "mins": 80, "diff": "medium", "q": 5, "res": ["Bit Hacks"]},
        {"topic": "REST API", "subtopic": "RESTful API Design Best Practices, Status Codes & JWT Authentication", "mins": 50, "diff": "medium", "q": 4, "res": ["RESTful API Guide"]},
    ]},
    {"focus": ["System Design", "Aptitude"], "tasks": [
        {"topic": "System Design", "subtopic": "Design a Notification System (Push, Email, SMS with Message Queues)", "mins": 90, "diff": "hard", "q": 3, "res": ["Message Queues Kafka/RabbitMQ"]},
        {"topic": "Aptitude", "subtopic": "Logical Deductions, Blood Relations & Syllogisms", "mins": 45, "diff": "medium", "q": 5, "res": ["IndiaBIX Logical"]},
    ]},
    {"focus": ["DSA", "Behavioral"], "tasks": [
        {"topic": "DSA", "subtopic": "Company-Specific Hard Problems: Amazon / FAANG Frequency Sheet", "mins": 100, "diff": "hard", "q": 4, "res": ["LeetCode Company Tags"]},
        {"topic": "Behavioral", "subtopic": "Company Leadership Principles & Behavioral Story Polishing", "mins": 40, "diff": "medium", "q": 3, "res": ["Amazon Leadership Principles"]},
    ]},
    {"focus": ["System Design", "DBMS"], "tasks": [
        {"topic": "System Design", "subtopic": "Low-Level Design (LLD): Design Parking Lot / Elevator System", "mins": 100, "diff": "hard", "q": 2, "res": ["LLD Practice Problems"]},
        {"topic": "DBMS", "subtopic": "SQL Performance Tuning & Execution Plans", "mins": 40, "diff": "hard", "q": 3, "res": ["SQL Tuning"]},
    ]},
    {"focus": ["DSA", "Communication"], "tasks": [
        {"topic": "DSA", "subtopic": "Mock DSA Coding Round under 45-minute timed constraints", "mins": 90, "diff": "hard", "q": 3, "res": ["LeetCode Contest"]},
        {"topic": "Communication", "subtopic": "Thinking Out Loud: Verbalizing edge cases, time/space complexity", "mins": 40, "diff": "medium", "q": 2, "res": ["Interview Communication Guide"]},
    ]},
    {"focus": ["DSA", "Aptitude"], "tasks": [
        {"topic": "DSA", "subtopic": "Revision: Tricky Edge Cases in Strings, Trees and DP", "mins": 90, "diff": "hard", "q": 6, "res": ["DSA Cheatsheet"]},
        {"topic": "Aptitude", "subtopic": "Full Length Aptitude Simulation Test", "mins": 50, "diff": "hard", "q": 25, "res": ["Aptitude Test"]},
    ]},

    # Phase 4: Mock Interviews & Final Readiness (Days 26–30)
    {"focus": ["Mock Interview", "DSA"], "tasks": [
        {"topic": "Mock Interview", "subtopic": "Technical Mock Interview 1: DSA (1 Medium + 1 Hard) with Live Code Review", "mins": 90, "diff": "hard", "q": 2, "res": ["PrepCopilot Mock Interview Module"]},
        {"topic": "Behavioral", "subtopic": "HR & Behavioral Mock Round (STAR framework)", "mins": 45, "diff": "medium", "q": 4, "res": ["PrepCopilot Behavioral"]},
    ]},
    {"focus": ["Mock Interview", "System Design"], "tasks": [
        {"topic": "Mock Interview", "subtopic": "Technical Mock Interview 2: System Design & CS Fundamentals", "mins": 90, "diff": "hard", "q": 3, "res": ["PrepCopilot Mock Interview Module"]},
        {"topic": "Communication", "subtopic": "Q&A with Interviewer & Architecture Defense", "mins": 40, "diff": "medium", "q": 2, "res": ["Interview Q&A Strategy"]},
    ]},
    {"focus": ["Revision"], "tasks": [
        {"topic": "Revision", "subtopic": "CS Fundamentals Flash Review: OS, DBMS, CN & OOP Top 50 Questions", "mins": 90, "diff": "easy", "q": 20, "res": ["CS Fundamentals Handbook"]},
        {"topic": "DSA", "subtopic": "Blind 75 Top Pattern Formulas & Complexity Matrix", "mins": 45, "diff": "easy", "q": 5, "res": ["Blind 75 Cheatsheet"]},
    ]},
    {"focus": ["Revision", "Behavioral"], "tasks": [
        {"topic": "Revision", "subtopic": "Resume Projects Deep Dive: Answering architectural trade-offs & design choices", "mins": 80, "diff": "medium", "q": 4, "res": ["Resume Review"]},
        {"topic": "Behavioral", "subtopic": "Final Behavioral & Culture Fit Rehearsal", "mins": 45, "diff": "easy", "q": 4, "res": ["HR Round Cheatsheet"]},
    ]},
    {"focus": ["Revision"], "tasks": [
        {"topic": "Revision", "subtopic": "Confidence Building, Mindset & Placement Day Strategic Checklist", "mins": 60, "diff": "easy", "q": 2, "res": ["Placement Day Checklist"]},
        {"topic": "Communication", "subtopic": "Final Self-Introduction (Elevator Pitch) Polish", "mins": 30, "diff": "easy", "q": 1, "res": ["Elevator Pitch Formula"]},
    ]},
]


def _build_curated_plan(
    target_role: str,
    target_company: Optional[str],
    timeline_days: int = 30,
    hours_per_day: float = 3.0,
    weak_skills: Optional[List[str]] = None,
    missing_skills: Optional[List[str]] = None,
) -> List[DayPlan]:
    """
    Deterministically builds an industry-grade, day-by-day roadmap tailored to the target role.
    Guarantees exactly `timeline_days` days with zero empty or missing tasks.
    """
    role_lower = (target_role or "").lower()
    is_data = any(w in role_lower for w in ["data", "analyst", "analytics", "bi", "business analyst", "statistic"])
    
    source_syllabus = DATA_ANALYST_SYLLABUS if is_data else SDE_SYLLABUS
    total_source = len(source_syllabus)
    
    # Subsample or scale to timeline_days
    selected_days = []
    if timeline_days == 7:
        indices = [0, 4, 9, 14, 19, 23, 29]
        selected_days = [source_syllabus[min(i, total_source - 1)] for i in indices]
    elif timeline_days == 14:
        indices = [int(i * (total_source - 1) / 13) for i in range(14)]
        selected_days = [source_syllabus[i] for i in indices]
    else:  # 30 days
        selected_days = source_syllabus[:timeline_days]
        # If needed to pad up to timeline_days
        while len(selected_days) < timeline_days:
            selected_days.append(source_syllabus[len(selected_days) % total_source])

    start_date = datetime.utcnow()
    day_plans = []

    # Time scale factor based on requested hours_per_day (default 2.5-3.0h = 150-180m)
    time_factor = max(0.5, min(2.0, (hours_per_day * 60) / 140))

    for idx, day_info in enumerate(selected_days):
        day_num = idx + 1
        day_date = (start_date + timedelta(days=idx)).strftime("%Y-%m-%d")
        
        tasks = []
        for t in day_info.get("tasks", []):
            scaled_mins = int(round(t.get("mins", 60) * time_factor / 5.0) * 5)
            tasks.append(
                DailyTask(
                    topic=t.get("topic", "General"),
                    subtopic=t.get("subtopic", "Core practice"),
                    duration_minutes=max(20, scaled_mins),
                    difficulty=t.get("diff", "medium"),
                    practice_questions=t.get("q", 5),
                    resources=t.get("res", ["Official Documentation", "Practice Problems"]),
                )
            )

        total_duration = sum(t.duration_minutes for t in tasks)
        day_plans.append(
            DayPlan(
                day=day_num,
                date=day_date,
                focus_areas=day_info.get("focus", ["Core Placement Topics"]),
                tasks=tasks,
                total_duration_minutes=total_duration,
                completed=False,
            )
        )

    return day_plans


async def generate_preparation_plan(
    user_id: str,
    skill_gap_id: str,
    timeline_days: int = 30,
    hours_per_day: float = 3.0,
) -> PreparationPlan:
    """
    Generate a full preparation plan from a skill gap analysis.
    Uses AI if available and merges with curated syllabus to guarantee complete, high-quality roadmaps.
    """
    # Fetch skill gap from DB
    db = get_database()
    skill_gap_doc = await db["skill_gaps"].find_one({"_id": ObjectId(skill_gap_id)})
    if not skill_gap_doc:
        raise ValueError(f"Skill gap analysis {skill_gap_id} not found")

    target_role = skill_gap_doc.get("target_role") or "Data Analyst"
    target_company = skill_gap_doc.get("target_company") or "Target Company"
    priority_order = skill_gap_doc.get("priority_order") or []
    weak_skills = skill_gap_doc.get("weak_skills") or []
    missing_skills = skill_gap_doc.get("missing_skills") or []

    # If priority order is empty, auto-populate reasonable defaults based on role
    if not priority_order:
        role_lower = target_role.lower()
        if any(w in role_lower for w in ["data", "analyst", "bi"]):
            priority_order = ["SQL", "Power BI", "Python", "Excel", "Tableau", "Statistics", "A/B Testing"]
        elif any(w in role_lower for w in ["frontend", "react"]):
            priority_order = ["JavaScript", "React", "TypeScript", "HTML/CSS", "State Management", "REST APIs"]
        else:
            priority_order = ["DSA", "SQL", "OOP", "DBMS", "Operating Systems", "System Design", "Aptitude"]

    # Build reliable base plan first as fallback/foundation
    curated_day_plans = _build_curated_plan(
        target_role=target_role,
        target_company=target_company,
        timeline_days=timeline_days,
        hours_per_day=hours_per_day,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
    )

    day_plans: List[DayPlan] = []

    # Try generating customized AI additions
    try:
        prompt = f"""Create a placement preparation plan for a student targeting "{target_role}" at "{target_company}".
Skills to cover: {', '.join(priority_order[:6])}
Weak skills: {', '.join(weak_skills) if weak_skills else 'None identified'}
Missing skills: {', '.join(missing_skills) if missing_skills else 'None identified'}
Timeline: {timeline_days} days. Available time: {hours_per_day} hours/day.

Return ONLY a JSON object with this key:
{{
  "days": [
    {{
      "day": 1,
      "focus_areas": ["SQL", "Data Analysis"],
      "tasks": [
        {{
          "topic": "SQL",
          "subtopic": "Joins and Aggregations",
          "duration_minutes": 60,
          "difficulty": "easy",
          "practice_questions": 5,
          "resources": ["SQL Practice Sheet", "W3Schools SQL"]
        }}
      ]
    }}
  ]
}}
"""
        raw_data = await chat_complete_json(
            [
                {"role": "system", "content": "You are an expert placement coach. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        days_raw = []
        if isinstance(raw_data, list):
            days_raw = raw_data
        elif isinstance(raw_data, dict):
            days_raw = (
                raw_data.get("days")
                or raw_data.get("plan")
                or raw_data.get("daily_plan")
                or raw_data.get("roadmap")
                or []
            )

        if isinstance(days_raw, list) and len(days_raw) >= (timeline_days // 2):
            start_date = datetime.utcnow()
            for d in days_raw:
                if not isinstance(d, dict):
                    continue
                tasks = []
                for t in d.get("tasks", []):
                    if not isinstance(t, dict):
                        continue
                    tasks.append(
                        DailyTask(
                            topic=str(t.get("topic", "General")),
                            subtopic=str(t.get("subtopic", "Core Concepts")),
                            duration_minutes=int(t.get("duration_minutes", 60)),
                            difficulty=str(t.get("difficulty", "medium")),
                            practice_questions=int(t.get("practice_questions", 5)),
                            resources=[str(r) for r in t.get("resources", []) if r],
                        )
                    )
                if not tasks:
                    continue

                day_num = int(d.get("day", len(day_plans) + 1))
                day_date = (start_date + timedelta(days=day_num - 1)).strftime("%Y-%m-%d")
                total_duration = sum(t.duration_minutes for t in tasks)

                day_plans.append(
                    DayPlan(
                        day=day_num,
                        date=day_date,
                        focus_areas=[str(f) for f in d.get("focus_areas", []) if f],
                        tasks=tasks,
                        total_duration_minutes=total_duration,
                    )
                )

    except Exception as e:
        logger.warning("AI plan generation note: %s. Using curated curriculum.", e)

    # If AI returned fewer days than requested (or failed completely), complete with curated curriculum
    if len(day_plans) < timeline_days:
        existing_days = {p.day for p in day_plans}
        for cur_p in curated_day_plans:
            if cur_p.day not in existing_days:
                day_plans.append(cur_p)
            if len(day_plans) == timeline_days:
                break
        day_plans.sort(key=lambda x: x.day)

    plan = PreparationPlan(
        user_id=user_id,
        skill_gap_id=skill_gap_id,
        target_role=target_role,
        target_company=target_company,
        timeline_days=timeline_days,
        days=day_plans,
        overall_progress=0.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return plan
