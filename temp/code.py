name = input("Name:")
salary = input("Salary:")

if salary.isdigit():
    salary = int(salary)
else:
    print("must input digit")
    exit()
    
msg = '''
    --------
    Name:   %s
    Salary: %s
    ''' %(name, salary)
    
print(msg)