---
name: reddit
description: Use this skill to browse Reddit, search subreddits, and read posts. Includes logic for handling login walls and popups. Reddit Browsing Skill. This skill enables the agent to operate a browser on reddit.com using the use_browser tool.
---

# 1. Command Syntax
The `use_browser` tool accepts arguments. Use the `agent-browser` skill reference.

`state load`: ALWAYS load the state
`--headed open`: ALWAYS launch the browser in headed mode to avoid anti-bot protection on Reddit.

# 2. Workflow & Login Handling
When accessing Reddit, you will likely encounter a "Login Wall" or "Open in App" popup. Follow this strict logic:

## Step 1: Initial Navigation
Command: `--headed open https://www.reddit.com`
Wait for the page to load.
## Step 2: Handle Login State (CRITICAL)
You can use saved `reddit.json` state in the `states` directory to operate reddit site. If the session not exists, you must cancel the operation and tell the user, that the state is not found.
Ensure that you're logged in.

## Step 3: Browsing Content

To go to a specific subreddit (e.g., 'python'):
Command: `--headed open https://www.reddit.com/r/python`

# 3. Research & Information Gathering Strategy
When the user asks for information (e.g., "latest news about LLM"), do NOT just look at the homepage. Follow
this deep-dive workflow:

**A. Identify Target Subreddits**
- For LLM/AI: Go to r/LocalLLaMA, r/MachineLearning, r/OpenAI, r/ArtificialInteligence.
- General: Use Reddit search if the specific subreddit is unknown.

**B. Sort by Relevance**
Do not rely on the default "Hot" feed if looking for recent updates.

- For Latest News: Sort by "New" to find breaking news.
- For Best Discussions: Sort by "Top" (e.g., Top of the Week).

How to sort: Look for the sort dropdown menu near the top of the subreddit list.

**C. Analyze Content Thoroughly**

1. Scan Titles: Use take_screenshot to see the feed.
2. Select Top Posts: Choose 3-5 relevant posts based on the user's request.
3. Read Post Body: Click the post title. Scroll through the text.
4. Check Comments: Scroll down to the comments section. Read the top comments to gauge community sentiment or find links to sources.
5. Extract Data: Note down titles, upvote counts, and key points from comments.

**D. Synthesis**
Combine findings from multiple posts/subreddits before answering the user. Do not provide a single-post summary unless asked.
