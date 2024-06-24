import csv
from collections import Counter
import matplotlib.pyplot as plt

with open("reviews.csv", mode="r") as file:
    reader = csv.DictReader(file)
    reviews = [row for row in reader]

license_dist = Counter()
len_reviews = len(reviews)
for index, review in enumerate(reviews):
    if review["license"] == "404":
        print(review["DOI"])
    license_dist.update([review["license"]])


if "" in license_dist:
    del license_dist[""]

most_common = license_dist.most_common(10)
print(most_common)
keys, values = zip(*most_common)

plt.bar(keys, values)
plt.title('Top 10 Most Common Licenses')
plt.xlabel('License')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('license_dist.png')