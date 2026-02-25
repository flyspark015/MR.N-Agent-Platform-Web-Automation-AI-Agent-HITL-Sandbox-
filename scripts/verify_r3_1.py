import asyncio
from core.research_service import discover_sources
from core.playbook_selector import PlaybookSelector

async def main():
    goal = "find drone manufacturers in India"
    urls = await discover_sources(goal)
    print("Test1 URLs:", urls[:5])
    print("Test1 OK:", all("google.com" not in u for u in urls))

    selector = PlaybookSelector()
    decision = await selector.classify("find suppliers for agricultural drone motors")
    print("Test2 decision:", decision)

    decision2 = await selector.classify("extract table of crop yields")
    print("Test3 decision:", decision2)

if __name__ == "__main__":
    asyncio.run(main())
