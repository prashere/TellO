list1 = [1, 2, 3]
list2 = list1
list1.append(4)
print(list2) # [1,2,3,4] because object is passed


x = 10
def modify_x():
    global x # If this excluded you get UnboundLocalError: local variable 'x' referenced before assignment
    x += 1
    print(x)

modify_x()



def foo(x=[]):
    x.append(1)
    return x
print(foo())  # [1]
print(foo())  # [1,1] because state is retained during function calls
# To avoid this behaviour use None math definition ma ani initialize the list fn block ma


a = (1, 2, 3)
b = (1, 2, 3)
print(a is b) # True because this is immutable and short tuple


a = [1, 2, 3]
b = [1, 2, 3]
print(a is b) # False Lists are mutable therefore not the same lists

print("------------")
print(True == 1)    # True
print(False == 0)   # True
print(True + True)  # 2
print(False + True) # 1


print("------------")
print(-3 ** 2)      # -9
print((-3) ** 2)    # 9

print("------------")
a = 3
b = 4
print(a and b)  # 4
print(a or b)   # 3
print(not a)    # False
# and returns the second value if both are truthy (3 and 4 → 4).
# or returns the first truthy value (3 or 4 → 3).
# not 3 returns False.

# If 1 var is made 0
print("------------")
a = 0
b = 4
print(a and b)  # 0
print(a or b)   # 4
print(not a)    # True

print("------------")
def func():
    pass
print(func()) # None

print("------------")
def fun():
    return 1
    return 2

print(fun()) # 1

print("------------")
print(type([]) is list) # True
print(type([]) == list) # True

print("------------")
print(0.1 + 0.2 == 0.3) # False
# Due to floating-point precision errors, 0.1 + 0.2 is actually 0.30000000000000004

print("------------")
a = 257
b = 257
print(a is b) # False
"""
Python caches integers from -5 to 256,
so numbers beyond that may not refer to the same object in memory.
"""


print("------------")
print('Lists || Sets || Tuples || Dicts || Strings')
print("------------")


print("------------")
list1 = [1, 2, 3]
list2 = list1
list2.append(4)
print(list1) # [1, 2, 3, 4]
print(list2) # [1, 2, 3, 4]

print("------------")
list1 = [1, 2, 3, 4]
list2 = list1[:]
list2.append(5)
print(list1) # [1, 2, 3, 4]
print(list2) # [1, 2, 3, 4, 5]

print("------------")
list1 = [1, [2, 3], 4]
list2 = list1[:]
list2[1].append(5)
print(list1) # [1, [2, 3, 5], 4]
print(list2) # [1, [2, 3, 5], 4]

print("------------")
# set1 = {1, 2, 3}
# set1.add([4, 5])
# print(set1) # TypeError

print("------------")
print("Python"[::-2]) # nhy





