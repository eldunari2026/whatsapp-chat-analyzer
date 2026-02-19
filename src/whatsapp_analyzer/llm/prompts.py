"""Prompt templates for WhatsApp chat analysis."""

# Single combined prompt — one LLM call instead of 3+N separate ones
ANALYZE_ALL = """Analyze this WhatsApp group chat. Respond ONLY in the exact format below, no extra text.

CHAT:
{chat_text}

Respond in this EXACT format:

SUMMARY:
(3-5 sentence summary of the conversation)

TOPICS:
- (topic 1)
- (topic 2)
- (add more as needed)

ACTION ITEMS:
- (Person: action item 1)
- (Person: action item 2)
- (add more as needed)

PARTICIPANTS:
{participant_list}"""

# Template for each participant line in the combined prompt
PARTICIPANT_LINE = "- {name}: (1-2 sentence summary of their contributions)"

# Kept for backward compat and chunked analysis
SUMMARIZE = """You are analyzing a WhatsApp group chat conversation. Provide a concise summary of the conversation covering the main discussion points and outcomes.

CHAT:
{chat_text}

Provide a clear summary in 3-5 sentences. Focus on what was discussed, decided, and any important information shared."""

EXTRACT_TOPICS = """You are analyzing a WhatsApp group chat conversation. Extract the key topics discussed.

CHAT:
{chat_text}

List each distinct topic on its own line, prefixed with "- ". Only list topics, no other text. Example:
- Project timeline discussion
- Backend API setup"""

EXTRACT_ACTION_ITEMS = """You are analyzing a WhatsApp group chat conversation. Extract any action items, tasks, or commitments made by participants.

CHAT:
{chat_text}

List each action item on its own line, prefixed with "- ". Include who is responsible if mentioned. Only list action items, no other text. Example:
- Bob: Set up the GitHub repository
- Alice: Review the PR by Friday"""

PARTICIPANT_ANALYSIS = """You are analyzing a WhatsApp group chat conversation. Analyze the contributions of a specific participant.

PARTICIPANT: {participant}

CHAT:
{chat_text}

In 2-3 sentences, describe what this participant contributed to the conversation, their main points, and any commitments they made."""

MERGE_SUMMARIES = """You are combining multiple summaries of different parts of a long WhatsApp group chat conversation into one cohesive summary.

PARTIAL SUMMARIES:
{summaries}

Combine these into a single coherent summary in 3-5 sentences. Remove redundancy and focus on the overall narrative."""

MERGE_TOPICS = """You are combining topic lists extracted from different parts of a WhatsApp conversation. Deduplicate and consolidate them.

TOPIC LISTS:
{topics}

Output a single consolidated list of unique topics, one per line prefixed with "- ". Remove duplicates and merge similar topics."""

MERGE_ACTION_ITEMS = """You are combining action item lists from different parts of a WhatsApp conversation. Deduplicate and consolidate them.

ACTION ITEM LISTS:
{action_items}

Output a single consolidated list of unique action items, one per line prefixed with "- ". Remove duplicates."""
