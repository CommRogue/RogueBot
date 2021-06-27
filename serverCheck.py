import math
def recurse(n = 5, currentNumber = 1, currentIndex = 1):
    print(currentNumber)
    if currentIndex <= n:
        recurse(n, currentNumber+(currentIndex), currentNumber+1)


def recurse2(arr = (1,4,1,12,7,19,4,5,8,11), firstIndex = 0, lastIndex = 9):
    if lastIndex-firstIndex <= 1:
        return max(arr[firstIndex], arr[lastIndex])
    return max(recurse2(arr, firstIndex, math.ceil((lastIndex-firstIndex)/2)+firstIndex), recurse2(arr, math.ceil((lastIndex-firstIndex)/2)+1+firstIndex, lastIndex))

def recurse3(arr = (1,5,4,8,5), additionArr = (True,True,True,True,True)):
    sum = 0

def recurse4(arr, additionArr):




print(recurse3())