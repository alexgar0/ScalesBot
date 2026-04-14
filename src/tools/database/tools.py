
import uuid

from pydantic_ai import RunContext

from tools._internal.registry import tool
from tools.database.deps import DatabaseDeps
from tools.database.models import MemoryEntry


@tool()
def search_knowledge(ctx: RunContext[DatabaseDeps], query: str, category: str | None = None) -> str:
    """Searches the knowledge database for relevant information fragments matching the given query.
    
    Call this tool when you need to retrieve factual data, contextual background, or specific details 
    from the stored knowledge base. Always formulate a concise, targeted query for optimal retrieval.
    
    Args:
        query (str): The search query. Should be specific and focused on the exact information needed. 
                     Avoid vague or overly broad phrasing.
        category (str | None, optional): Filters results to a specific knowledge domain (e.g., 'technical', 
                                         'policies', 'user_manual'). Leave as None for a cross-domain search.
                                         
    Returns:
        str: A newline-separated list of up to 3 matching fragments in the exact format:
             "[{type}] (score:{score:.2f}) {content}". 
             Returns "NO_RESULTS" if no matching entries are found. Parse scores to weigh relevance 
             when multiple fragments are returned.
    """
    results = ctx.deps.repo.search(query, top_k=3, category=category)
    if not results:
        return "NO_RESULTS"
    return "\n".join(
        f"[{r['meta'].get('type','doc')}] (score:{r['score']:.2f}) {r['content']}"
        for r in results
    )

@tool()
def save_memory(ctx: RunContext[DatabaseDeps], memory_entry: MemoryEntry) -> str:
    """Stores a structured episodic long-term memory entry for future retrieval and context retention.
    
    Call this tool when you encounter information that should persist across sessions, such as:
    - Explicit user preferences, constraints, or feedback
    - Key decisions, action items, or unresolved issues
    - Factual takeaways or domain-specific context not present in the knowledge base
    
    Args:
        memory_entry (MemoryEntry): A structured object containing the memory content and metadata.
                                    Ensure it is concise, self-contained, and follows the expected 
                                    MemoryEntry schema (e.g., includes timestamp, tags, or context 
                                    fields if required by your implementation).
                                    
    Returns:
        str: "SAVED" upon successful persistence. Do not assume the entry is retrievable until 
             confirmed by subsequent search calls.
    """
    ctx.deps.repo.store(entry=memory_entry, entry_id=str(uuid.uuid4()))
    return "SAVED"