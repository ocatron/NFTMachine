import random
from collections import Counter
import bisect
import time
from pathlib import Path

# Select an index based on rarity weights
def select_index(cum_rarities, rand):
    
    cum_rarities = [0] + list(cum_rarities)
    for i in range(len(cum_rarities) - 1):
        if rand >= cum_rarities[i] and rand <= cum_rarities[i+1]:
            return i
    
    # Should not reach here if everything works okay
    return None



my_nums = {'A': 5, 'B': 2, 'C': 2, 'D': 1}


def weighted_random_si(nums):
    cum_weight = []
    sum = 0

    for weight in my_nums.values():
        sum += weight
        cum_weight.append(sum)

    r = random.random()*sum

    #idx = bisect.bisect_right(cum_weight,r,0,3)
    idx = select_index(cum_weight,r)
    return list(my_nums.keys())[idx]

def weighted_random_bisect(nums):
    cum_weight = []
    sum = 0

    for weight in my_nums.values():
        sum += weight
        cum_weight.append(sum)

    r = random.random()*sum

    idx = bisect.bisect_right(cum_weight,r,0,3)
    return list(my_nums.keys())[idx]


rounds = 10000000

# Check out the results
# start = time.time()
# result1 = Counter(weighted_random_bisect(my_nums) for _ in range(rounds))
# print(time.time()-start)

# start = time.time()
# result2 = Counter(weighted_random_bisect(my_nums) for _ in range(rounds))
# print(time.time()-start)


# print(result1)
# print(result2)
# count = 1000
# zFillLen = len(str(count))
# print(zFillLen)

# print(str(45).zfill(zFillLen))

# statement = "somename.png"
# statement = None
# statement = ""

# if statement is not None:
#     print("Done")
# else:
#     print("skipped")

comp = [0,1,2,3,4,5]

for layer in comp[1:]:
    print(layer)