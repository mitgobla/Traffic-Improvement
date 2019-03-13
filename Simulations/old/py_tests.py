array = [0,0,1,1,1,1,2,2,2,2,3,3]

indexEqualCurrentUsage = []

for index in range(len(array)):
    if array[index] == 1:
        indexEqualCurrentUsage.append(index)

print(indexEqualCurrentUsage)