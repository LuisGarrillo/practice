#include <iostream>
#include <cmath>
#include <cctype>

bool is_digit(char *str);
void print_narcissist(int amount);

int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <number>" << std::endl;
        return 1;
    }
    else if(!is_digit(argv[1])) {
        std::cout << "Usage: " << argv[0] << " <number>" << std::endl;
        return 1;
    }

    print_narcissist(std::stoi(argv[1]));

    return 0;
    
}

bool is_digit(char *str) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (!isdigit(str[i])) {
            return false;
        }
    }
    return true;
}

void print_narcissist(int amount) {
    
    for (int i = 1; amount > 0; i++) {
        int digits = {};
        int aux_value = i;

        while (aux_value > 0) {
            aux_value /= 10;
            digits++;
        }

        aux_value = i;
        int sum {};

        while (aux_value > 0) {
            int digit = aux_value % 10;
            aux_value /= 10;
            sum += pow(digit, digits);
        }

        if (sum == i) {
            std::cout << i << std::endl;
            amount--;
        }
    }  
}