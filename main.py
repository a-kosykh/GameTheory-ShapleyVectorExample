import itertools
import math

from bitarray import bitarray
from bitarray import util
from itertools import combinations
from math import factorial


class CoopGame:
    def __init__(self, char_func_dict):
        self.char_func = char_func_dict
        self.empty_bitarray = bitarray('0000')
        self.players = 4
        self.shapley_vector = None

    def __print_game(self):
        for coalition in self.char_func:
            print(f"{self.__bitarray_notation(coalition)}: ", self.char_func[coalition])

    def __bitarray_notation(self, str_bitarray) -> str:
        rv = "v({"
        for i in range(len(str_bitarray)):
            if str_bitarray[i] == "1":
                rv += str(i+1)
        rv += "})"
        return rv

    def __is_comb_subset(self, comb):
        for coalition_i in comb:
            for coalition_j in comb:
                if coalition_i == coalition_j:
                    continue
                if bitarray(coalition_i) & bitarray(coalition_j) != self.empty_bitarray:
                    return True
        return False

    def __check_super_additive(self) -> bool:
        combination_list = []
        for i in range(2, 4+1):
            combination_list += list(map(dict, combinations(self.char_func.items(), i)))
        disjoint_combinations = []
        for comb in combination_list:
            if not self.__is_comb_subset(comb):
                disjoint_combinations.append(comb)
        for comb in disjoint_combinations:
            union = bitarray('0000')
            disjoint_value_sum = 0
            for coalition in comb:
                union |= bitarray(coalition)
                disjoint_value_sum += self.char_func[coalition]
            if disjoint_value_sum > self.char_func[union.to01()]:
                print_rv = "\nИгра не супераддитивна: "
                print_rv += f"{self.__bitarray_notation(union.to01())} < "
                i = 0
                for coal_i in comb:
                    print_rv += self.__bitarray_notation(coal_i)
                    i += 1
                    if i != len(comb):
                        print_rv += " + "
                print_rv += f" ({self.char_func[union.to01()]} < {disjoint_value_sum})"
                print(print_rv)
                print(f"Изменяем: {self.__bitarray_notation(union.to01())} --> {disjoint_value_sum}")

                self.char_func[union.to01()] = disjoint_value_sum
                return False
        print("\nТеперь игра супераддитивна! (づ｡◕‿‿◕｡)づ")
        return True

    def __check_convex(self):
        combination_list = list(map(dict, combinations(self.char_func.items(), 2)))
        for comb in combination_list:
            union = bitarray('0000')
            intersection = bitarray('1111')
            value_sum = 0
            for coalition in comb:
                union |= bitarray(coalition)
                intersection &= bitarray(coalition)
                value_sum += self.char_func[coalition]
            if self.char_func[union.to01()] + self.char_func[intersection.to01()] < value_sum:
                print_rv = f"\nИгра не является выпуклой: {self.__bitarray_notation(union.to01())} + " \
                           f"{self.__bitarray_notation(intersection.to01())} < "
                i = 0
                for coal in comb:
                    print_rv += self.__bitarray_notation(coal)
                    i += 1
                    if i != len(comb):
                        print_rv += " + "
                print_rv += f" ({self.char_func[union.to01()] + self.char_func[intersection.to01()]} < {value_sum})"
                print(print_rv)
                return False
        print("Игра выпукла!")
        return True

    def __shapley_value(self, i):
        default_coalition = bitarray('1000')
        for j in range(i - 1):
            default_coalition >>= 1

        temp_list = []
        for coalition in self.char_func:
            if bitarray(coalition) & default_coalition != self.empty_bitarray:
                temp_list.append(coalition)

        temp_list2 = []
        for i in range(1, self.players + 1):
            one_size_array = []
            for coalition in temp_list:
                if bitarray(coalition).count(1) == i:
                    one_size_array.append(coalition)
            temp_list2.append(one_size_array)

        shapley_value = 0
        for i in temp_list2:
            sum_one_count = 0
            for j in i:
                v_s = bitarray(j)
                s_no_i = v_s ^ default_coalition
                sum_one_count += self.char_func[v_s.to01()] - self.char_func[s_no_i.to01()]
            sum_one_count *= factorial(bitarray(i[0]).count(1) - 1) * factorial(self.players - bitarray(i[0]).count(1))
            shapley_value += sum_one_count
        shapley_value /= factorial(self.players)
        return shapley_value

    def __shapley_vector(self) -> list:
        shapley_vector = []
        for i in range(1, self.players + 1):
            shapley_vector.append(self.__shapley_value(i))
        return shapley_vector

    def __check_individual_ratio(self) -> bool:
        def_bit_array = bitarray("1000")
        for elem in self.shapley_vector:
            if elem < self.char_func[def_bit_array.to01()]:
                return False
            def_bit_array >>= 1
        return True

    def __print_shapley_vector_info(self):
        if self.shapley_vector is None:
            return
        formatted_shapley_vector = [round(elem, 5) for elem in self.shapley_vector]
        print(f"\nВектор Шепли: {formatted_shapley_vector}")
        if math.isclose(sum(self.shapley_vector), self.char_func['1111']):
            print_rv = "Выполняется свойство групповой рационализации: "
            i = 0
            for coalition in self.char_func:
                if bitarray(coalition).count(1) == 1:
                    i += 1
                    print_rv += self.__bitarray_notation(coalition)
                    if i != self.players:
                        print_rv += " + "
                    else:
                        break
            print_rv += " = "
            print_rv += self.__bitarray_notation('1111')
            print_rv += f" ({round(sum(self.shapley_vector))} = {self.char_func['1111']})"
            print(print_rv)
        print(f"Выполняется свойство индивидульной рационализации: {self.__check_individual_ratio()}")


    def i_solve(self):
        self.__print_game()
        while not self.__check_super_additive():
            ...
        self.__print_game()
        self.__check_convex()
        self.shapley_vector = self.__shapley_vector()
        self.__print_shapley_vector_info()


def fill_char_func() -> dict:
    char_dict = {
        bitarray('0000').to01(): 0,
        bitarray('1000').to01(): 3,
        bitarray('0100').to01(): 2,
        bitarray('0010').to01(): 3,
        bitarray('0001').to01(): 2,
        bitarray('1100').to01(): 6,
        bitarray('1010').to01(): 6,
        bitarray('1001').to01(): 5,
        bitarray('0110').to01(): 6,
        bitarray('0101').to01(): 4,
        bitarray('0011').to01(): 7,
        bitarray('1110').to01(): 10,
        bitarray('1101').to01(): 10,
        bitarray('1011').to01(): 9,
        bitarray('0111').to01(): 10,
        bitarray('1111').to01(): 12
    }
    return char_dict


if __name__ == '__main__':
    c1 = CoopGame(fill_char_func())
    c1.i_solve()
    '''
    b1 = bitarray('0100')
    b2 = bitarray('0001')
    b3 = b1 & b2
    print(b3 == bitarray("0000"))
    '''



