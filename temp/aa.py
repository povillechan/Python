# name = input("Name:")
# salary = input("Salary:")
# 
# if salary.isdigit():
#     salary = int(salary)
# else:
#     print("must input digit")
#     exit()
#     
# msg = '''
#     --------
#     Name:   %s
#     Salary: %s
#     ''' %(name, salary)
#     
# print(msg)
def func(arg,li=[]):
    print(id(li))
    li.append(arg)
    return li

v1 = func(1)
print(v1)
print(id(v1))
v2 = func(2,[])
print(v2)
v3 = func(3)
print(v3)