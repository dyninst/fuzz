# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <unistd.h>
# include <sys/types.h>
// # include <linux/limits.h>
int main( int argc, char *argv[] )
{

	char buf[100];

	while(scanf("%s", buf)) {
		if(strcmp(buf, "quit") == 0) {
			return 0;
		}

		else if(strcmp(buf, "bus_mac") == 0) {
			char* filename = "hahaha";
			filename[0] = 'a';

			// int *iptr;
			// char *cptr;
			// cptr = malloc(sizeof(int) + 1);
			// iptr = (int *) ++cptr;
			// *iptr = 42;

			// unsigned char data[6];
			// (unsigned int *) (data + 2) = 0xdeadf00d;

			// char buf[3];
			// sprintf(buf,"123456\n");
			// short array[16];
			// int * p = (int *) &array[1];
			// *p = 1;
		}
		else if(strcmp(buf, "bus_linux") == 0) {
			//char* filename = "hahaha";
			//filename[0] = 'a';

			int *iptr;
			char *cptr;
			cptr = malloc(sizeof(int) + 1);
			iptr = (int *) ++cptr;
			*iptr = 42;

			//unsigned char data[6];
			//(unsigned int *) (data + 2) = 0xdeadf00d;

			 char buf[3];
			 sprintf(buf,"123456\n");
			 short array[16];
			 int * p = (int *) &array[1];
			 *p = 1;
		}
		else if(strcmp(buf, "segment") == 0) {
			// int arr[2]; 
			// arr[3] = 10;
			int *p = 0; 
			printf("%d",*p); 
		}
		else {
			printf("buf is %s\n", buf);
		}
	}
}
