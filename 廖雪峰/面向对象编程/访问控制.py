# -*- coding:utf-8 -*-
'''
@author: chenzf
'''

class Student1(object):    
    def __init__(self, name, age):
        self.__name = name
        self.__age = age
        
    def age(self):
        return self.__age

obj=Student1("alex", 15)
obj.__age = 99
print(obj.age())

obj._Student1__age = 90
print(obj.age())


class Student(object):   
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
    
    def get_gender(self):
        return self.gender
    
    def set_gender(self, gender):
        self.gender = gender
 
# 测试:
bart = Student('Bart', 'male')
if bart.get_gender() != 'male':
    print('测试失败!')
else:
    bart.set_gender('female')
    if bart.get_gender() != 'female':
        print('测试失败!')
    else:
        print('测试成功!')