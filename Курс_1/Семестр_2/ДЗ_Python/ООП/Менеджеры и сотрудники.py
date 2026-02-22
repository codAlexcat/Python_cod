class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Employee(Person):
    def __init__(self, name, age, position):
        super().__init__(name, age)
        self.position = position

    def get_info(self):
        return f"\nИмя: {self.name} \nВозраст: {self.age} \nДолжность: {self.position} \n"

class Manager(Employee):
    def __init__(self, name, age, position):
        super().__init__(name, age, position)
        self.team = []

    def add_team(self, employee):
        self.team.append(employee)
        print(f"{employee.name} добавлен в команду {self.team}")

    def show_team(self):
        print(f"Команда менеджера: {self.team}")
        for emp in self.team:
            print(f"- {emp.name} ({emp.position})")

employees = {}

while True:
    print(" -- 1. Добавить сотрудника | 2. Добавить менеджера | 3. Назначить в команду | 4. Показать всех | 5. Выход")
    choice = input("Выберите действие: ")

    try:
        if choice == "1" or choice == "2":
            name = input("Введите имя: ")
            age = input("Введите возраст: ")
            pos = input("Введите должность:")

            if choice == "1":
                employees[name] = Employee(name, age, pos)
            else:
                employees[name] = Manager(name, age, pos)
            print("Успешно добавлено ^-^ ")

        elif choice == "3":
            name_m = input("Имя менеджера: ")
            name_e = input("Имя сотрудника: ")

            manager = employees.get(name_m)
            worker = employees.get(name_e)

            if isinstance(manager, Manager) and worker:
                manager.add_team(worker)
            else:
                print("Ошибка: не найден менеджер или сотрудник -_-! ")

        elif choice == "4":
            for emp in employees.values():
                print(emp.get_info())
                if isinstance(emp, Manager):
                    print(f" -- {emp.show_team()}")

        elif choice == "5":
            break
    except ValueError:
        print("Ошибка: Возраст должен быть числом -_-!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
