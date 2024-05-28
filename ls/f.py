# Бекболот

# классы понятие ООП, GIT
# PEP8 SOLID ООП
# Объектно ориентированное программирование

# PEP8 SOLID ООП
# ОБЬЕКТНО ориентированное программирование

p='p',1,1.2,True,[],{},(),None

print(type(p))


#
class Human:
    # свойствО класса
    глаза=2

    def __init__(self,name,age):
        self.name=name
        self.возраст=age
    # метод
    def test(self):
        print(self.глаза)

#     магический метод
    def __str__(self):
        return (f'имя : {self.name}\n'
                f'возраст : {self.возраст}\n'
                f'-----------------------\n')



# def test():
#     print('глаза')
#
# test()

# экземпляр \ обьект класса
beka=Human('beka',20)
beka1=Human('beka',21)
beka2=Human('beka',22)
beka3=Human('beka',69)
# print(beka,beka2,beka3,beka1)
print(type(beka))
print(len(beka))


# Human.test(beka)