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
from functools import reduce
result = reduce(lambda x,y: str(x)+' '+ str(y), ('霸刀5', '逍遥一刀1', 177200685, 1585290, 101, 55))
print(result)