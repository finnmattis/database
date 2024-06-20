import csv
from collections import Counter
import matplotlib.pyplot as plt

with open("reviews.csv", mode="r") as file:
    reader = csv.DictReader(file)
    reviews = [row for row in reader]

license_dist = Counter()
for index, review in enumerate(reviews[:5000]):
    license_dist.update([review["license"]])


if "" in license_dist:
    del license_dist[""]

most_common_l = license_dist.most_common(10)
keys_l, values_l = zip(*most_common_l)

plt.bar(keys_l, values_l)
plt.title('Top 10 Most Common Licenses')
plt.xlabel('License')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('license_dist.png')