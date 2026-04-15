from book_fetcher import search_book_metadata
from agent import Agent

# result = search_book_metadata("A empregada")
# print(result)

agent = Agent()
result = agent.recommend(
    ["The Housemaid Freida McFadden"]
)
print(result)
