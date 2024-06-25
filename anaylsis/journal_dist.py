import csv
from collections import Counter
import matplotlib.pyplot as plt

with open("reviews.csv", mode="r") as file:
    reader = csv.DictReader(file)
    reviews = [row for row in reader]

journal_dist = Counter()
for index, review in enumerate(reviews):
    journal_dist.update([review["Journal"]])

most_common = journal_dist.most_common(20)
keys, values = zip(*most_common)

plt.bar(keys, values)
plt.title('Top 20 Most Common Journals')
plt.xlabel('Journal')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('journal_dist.png')

