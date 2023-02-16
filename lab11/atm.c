#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

/**
 * Opis ataku
 * 
 * Dla typu int, na 32 bicie trzymana jest informacja o znaku.
 * Dla ujemnych liczb wykorzystywana jest notacja dopełnienia do dwóch (U2) 
 * 
 * Dla typu uint, najstarszy bit pełni funkcję jak każdy inny, w konsekwencji
 * rozszerzając maksymalną wartość 2x w porównaniu do typu int
 * 
 * (32 bit) 2^31 = 2147483648
 * 2^31 + 100 + 1 = 2147483749
 * 
 * W momencie kiedy dokonywana jest operacja odejmowania na typach uint i int,
 * typ int jest castowany na uint przez co bit znaku przestaje reprezentować znak.
 * Po operacji, wynik jest castowany ponownie na typ int (przez '%d'). Najstarszy
 * bit staje się bitem znaku.
 * 
 *              100 := 0000 0000 0000 0000 0000 0000 0110 0100
 *       2147483749 := 1000 0000 0000 0000 0000 0000 0110 0101
 *   U2(2147483749) := 0111 1111 1111 1111 1111 1111 1001 1011
 * 100 - 2147483749 <=> 100 + U2(2147483749)
 * 100 - 2147483749 := 0111 1111 1111 1111 1111 1111 1111 1111 -> 2147483647 (MAX_INT32)
 */

/**
 * Rozwiązanie
 * 
 * Poprawiki w komentarzach przy przerobionym kodzie
 */

int main(int argc, char** argv) {
	unsigned int pin;
	unsigned int amount;
	int balance = 100; // zastosować 'unsigned int' zamiast 'int'

	if (isdigit(argv[2][0]) == 0) {
		printf("Attach mitigated\n");
		exit(1);
	}

	sscanf(argv[1], "%u", &pin);
	sscanf(argv[2], "%u", &amount);

	if (pin != 1234) {
		printf("\033[31;1mPIN Invalid\033[0m\n");
		exit(2);
	} else {
		printf("\033[32;1mPIN Accepted\033[0m\n");
	}

	/**
	 * Walidacja możliwości wykonania operacji
	 * 
	 * if (balance < amount) {
	 *     printf("\033[31;1mInsufficient balance\033[0m\n");
	 *     exit(3);
	 * }
	 */

	printf("Deposit:\n");
	printf("%dBTC - %dBTC = %dBTC\n", balance, amount, balance - amount); // zmienić '%d' na '%u'
	return 0;
}
