# Lab 1: Add 2 numbers manually
# number1 = 100
# number2 = 22
# result = number1+number2
# print(f"This is the result : {result}") 
#Tip : select the lines you want to comment and hit cltrl + /

# Lab2 : Add 2 numbers dynamically like a calculator
number1 = input("Enter the first number: ")
number1_integer= int(number1) #type conversion

number2 = input("Enter the second number: ")
number2_integer= int(number2) #type conversion

result_string = number1+number2
print(f"This is the result_string : {result_string}")

result_int = number1_integer+number2_integer
print(f"This is the result_int : {result_int}")

#Homwork : Add 3 numbers and print the result
# question 2: Subtract 2 numbers and print the result
# question 3: Multiply 2 numbers and print the result
# question 4: Divide 2 numbers and print the result

# question 2: Subtract 2 numbers and print the result
number1 = input("Enter the first number: \n")
number1_integer= int(number1) #type conversion
number2 = input("Enter the second number: \n")
number2_integer= int(number2) #type conversion
result_subtract = number1_integer - number2_integer
print(f"\nThis is the \nresult_subtract : {result_subtract}")