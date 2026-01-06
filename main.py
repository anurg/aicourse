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
def make_adder(n):
    return lambda x: x+n
adder_3 = make_adder(3)
adder_5 = make_adder(5)
print(adder_3(10))
print(adder_5(10))