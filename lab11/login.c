#include <stdio.h>
#include <string.h>

int main(int argc, char** argv) {
	int zalogowany;
	char haslo[8];

	/**
	 * Opis ataku
	 *
	 * ./a.out $(printf "aaaabbbb\x01")
	 */

	/**
	 * Rozwiązanie 1 - dynamiczna alokacja pamięci
	 * Przeniesienie zmiennej hasło na heap ze stosu pozbędzie się problemu sąsiedztwa zmiennych
	 *  
	 * haslo = (char *)malloc(8 * sizeof(char));
	 * 
	 * Należy pamiętać o zwolnieniu tej pamięci
	 * free(haslo);
	 */

	/**
	 * Rozwiązanie 2 - walidacja danych wejściowych
	 * Dodanie warunku logicznego sprawdzającego długość podanego hasła
	 * 
	 * if (strlen(argv[1]) > 8) {
	 *     printf("NIE\n");
	 * 	   return 0;
	 * }
	 */

	zalogowany = 0;
	strcpy(haslo, argv[1]);
	if (strcmp(haslo, "Tajne") == 0)
		zalogowany = 1;
	if (zalogowany == 1)
		printf("TAK\n");
	else
		printf("NIE\n");
	return 0;
}
