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
import os
import re

def file_rename_1(path_name):
    for fpathe,dirs,fs in os.walk(path_name):
        for f in fs:
            path_cur = os.path.join(fpathe,f)
    #        print(path_cur)
            result = re.search('(.*?)_large.jpg', path_cur, re.S)
            if result:
                file_name = result.group(1)
                last_num = file_name.split('\\')[-1]
    
                dst_file = os.path.dirname(path_cur) + '\\' + str(int(last_num) + 1) + '_.jpg'
                
                print("%s ==> %s" %(path_cur, dst_file))
                
                os.rename(path_cur, dst_file)
                
                
      
                
def file_rename_2(path_name):
    for fpathe,dirs,fs in os.walk(path_name):
        for f in fs:
            path_cur = os.path.join(fpathe,f)
    #        print(path_cur)
            result = re.search('(.*?)_.jpg', path_cur, re.S)
            if result:
                file_name = result.group(1)

                dst_file = file_name + '.jpg'
                
                print("%s ==> %s" %(path_cur, dst_file))
                
                os.rename(path_cur, dst_file)  
    
    
def file_rename_bat(path_name):
    file_rename_1(path_name)
    file_rename_2(path_name)
    
    
    
    
file_rename_bat("D:\\Pictures\\18OnlyGirls\\movies")
