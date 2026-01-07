# import logging

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s-%(message)s')

# logging.debug('Start of the Program')
# def factorial(n):
#     logging.debug('Start of factorial(%s)' %(n))
#     total = 1
#     for i in range(1,n+1):
#         total *= i
#         logging.debug('i is '+str(i) + ', total is' + str(total))
#     logging.debug('End of factorial(%s)' %(n))
#     return total
# print(factorial(5))
# logging.debug('End of the Program')

# # lambda functions
# add = lambda x, y: x + y
# print(add(2,3))
# # unnamed lambda like immediately executed functions in JS
# print((lambda x,y : x * y) (5,4))

# ## Closure like in JS
# def make_adder(n):
#     return lambda x: x+n
# adder_3 = make_adder(3)
# adder_5 = make_adder(5)
# print(adder_3(10))
# print(adder_5(10))
# age = 18
# print('kid' if age<18 else 'adult')

# # args (arguments)
# def fruits(*args):
#     for fruit in args:
#         print(fruit)
# fruits("Apple","Guava","Mango")

# kwargs (key word arguments)
# def veg(**kwargs):
#     for key,value in kwargs.items():
#         print("{}:{}".format(key,value))
# if __name__=="__main__":
#     veg(name="Tomoato",color="Red",weight=5.5)

# # importing scripts and running individual scripts tests when running standalone
# import veg
# veg.veg(name="Potato",color="Brown", Size="Medium")

# #  map, filter,reduce
# l = [1,2,3,4]
# # # using lambda function
# # newl = map(lambda x:2 * x, l)
# # print(list(newl))
# # using normal function
# def nDouble(x):
#     return 2 * x
# newl = map(nDouble,l)
# print(list(newl))
# # filter
# l = [1,2,3,4]
# # def is_even(x):
# #     return x % 2 ==0
# # evenl= filter(is_even , l)
# evenl= filter(lambda x:x%2==0 , l)
# print(list(evenl))
# print(l)

# #reduce
# # Without reduce
# expenses = [
#     ("Dinner",100),
#     ("Car Repir",80),
#     ("Outing",180),
#     ("Party",53),
# ]
# # sum=0
# # for expense in expenses:
# #     sum +=expense[1]
# # print(sum)

# # With reduce
# from functools import reduce
# sum=reduce(lambda acc,b:acc+b[1],expenses,0)
# print(sum)

# #### Enums in Python
# from enum import Enum
# class State(Enum):
#     ACTIVE = 1
#     INACTIVE = 0
# member = State.ACTIVE
# print(member)
# print(repr(member))
# print(repr(member.name))
# print(repr(member.value))

# print([s.name for s in State])
# print([s.value for s in State])

# # Closure - The state of function is still alive even when the function is not longer referenced
# def counter():
#     count =0

#     def increment():
#         nonlocal count
#         count +=1
#         return count
#     return increment
# counter_1 = counter()
# counter_2 = counter()

# print(counter_1())
# print(counter_2())
# print(counter_1())
# print(counter_1())
# print(counter_2())

#### Objects
# age = 51
# print(age.real)
# print(age.imag)
# print(age.bit_length())
# print(age.bit_count())

# l = [2,8]
# l.append(15)
# l.pop()
# print(l)
# print(id(l))

# ##### Class and Inheritence
# class Animal:
#     def walk(self):
#         print("Walking..!")
# class Dog(Animal):
#     def __init__(self,name,age):
#         self.name = name
#         self.age = age
#     def bark(self):
#         print("woof")

# roger = Dog("Roger",7)
# roger.bark()
# roger.walk()
# print(roger.name)
# print(roger.age)