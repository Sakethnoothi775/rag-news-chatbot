import json

# Load articles
with open('data/articles.json', 'r') as f:
    articles = json.load(f)

print(f'Total articles: {len(articles)}')
print('\nArticle titles:')
for i, article in enumerate(articles[:10]):
    print(f'{i+1}. {article["title"]}')

print('\nTesting different queries...')
