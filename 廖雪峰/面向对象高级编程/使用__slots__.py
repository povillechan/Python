'''
Created on 2018年6月13日

@author: chenzf
'''
class Student(object):
    pass

s = Student()
s.age = 55
print(s.age)

def set_age(self, age):
    self.age = age
    
from types import MethodType
s.set_age = MethodType(set_age, s)
s.set_age(5)

q = Student()
print(s.age) 
#print(q.age) ->error

Student.set_age = set_age
p = Student()
p.set_age(66)
print(p.age) 

class Student2(object):
    __slot__ = ('name','age') #仅对当前类实例起作用，对继承的子类是不起作用的

s2 = Student2()
s2.name = "alex"
s2.age = 66
#s2.score = 99 ->error


class GraduateStudent(Student2):
    pass
g = GraduateStudent()
g.score = 99
