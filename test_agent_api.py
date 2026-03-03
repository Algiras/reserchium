import asyncio
from llama_index.core.agent import ReActAgent
from llama_index.llms.ollama import Ollama

async def main():
    llm = Ollama(model="mistral-small3.2", base_url="http://localhost:11434")
    agent = ReActAgent(name="agent", tools=[], llm=llm)
    # Using run with user_msg
    res = await agent.run(user_msg="What is the capital of France?")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
