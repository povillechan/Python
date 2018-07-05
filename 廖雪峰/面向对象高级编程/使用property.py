
'''
Created on 2018年6月13日

@author: chenzf
'''
class Student(object):

    @property
    def birth(self):
        return self._birth

    @birth.setter
    def birth(self, value):
        self._birth = value

    @property
    def age(self):
        return 2015 - self._birth


s  = Student()
s.birth = "aa"
#s.age = 16 -> AttributeError: can't set attribute



