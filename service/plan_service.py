from datetime import datetime, timezone

import anthropic
from pymongo import MongoClient
from service.context_service import clean_text
from service.tools.constants import ANTHROPIC_API_KEY, MONGODB_URI
from service.tools.tooling import tools_schema
from dto.plan_dto import MemorySchema, PlanOutputSchema
from prompts.system_prompts import planning_system_prompt

# Initialize the Anthropic and Mongo Client
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize MongoDB client and collection
mongo_client = MongoClient(MONGODB_URI)
database = mongo_client["database"]
memory_collection = database.get_collection("memory")
conversation_collection = database.get_collection("conversation")

# Insert what is happeneing (conversations tool calls )
def insert_conversation_events(sessionId, userId, role, content, tokens, eventType):
    conversation_collection.insert_one({
        "sessionId": sessionId,
        "userId": userId,
        "role": role,
        "type": eventType,
        "content": content,
        "tokens": tokens,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
# Create plan first, of what to do with the document and add the current plan to the memory
def gather_context_and_plan(user_prompt, user_id, thread_id):
    response = anthropic_client.messages.create(
        model="claude-opus-4-5",
        messages=[{"role": "user", "content": planning_system_prompt + user_prompt}],
        tools=tools_schema,
        output_config=PlanOutputSchema
    )

    insert_conversation_events(
        sessionId=thread_id,
        userId=user_id,
        role="assistant",
        content=response.content[0].text,
        tokens=response.usage.total_tokens,
        eventType="plan_generation"
    )
    return response.content[0].text


# Generate action subagents that are orchestrated by the main agent based on the current plan in memory