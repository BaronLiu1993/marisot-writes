
# Create tools with them such as MCP, use only recognisable journals and databases for the web search tool
def web_search_tool(query):
    pass

# Generate subagents based on the plan purpose, only if they can run in parallel
def generate_subagent(user_id, thread_id, purpose, context):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "Generate an action agent based on the current plan in the memory and the tools available."}],
        output_config=
    )
    return response.content[0].text
