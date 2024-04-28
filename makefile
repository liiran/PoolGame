all: libphylib.so _phylib.so

phylib.o: phylib.c phylib.h
	clang -std=c99 -Wall -pedantic -fpic -c phylib.c

libphylib.so: phylib.o
	clang -shared -o libphylib.so phylib.o -lm

phylib_wrap.c phylib.py: phylib.i
	swig -python phylib.i

phylib_wrap.o: phylib_wrap.c
	clang -std=c99 -Wall -pedantic -c phylib_wrap.c -I/usr/include/python3.10/ -fPIC -o phylib_wrap.o
	
_phylib.so: phylib_wrap.o libphylib.so
	clang -Wall -pedantic -std=c99 -shared phylib_wrap.o -L. -L/usr/lib/python3.10 -lpython3.10 -lphylib -o _phylib.so

clean:
	rm *.o *.so phylib_wrap.c phylib.py
