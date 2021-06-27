def recurse(count) -> float:
    if count == 500:
        return 0
    return 1/(2+recurse(count+1))

print(recurse(0))