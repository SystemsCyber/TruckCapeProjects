# SPDX-License-Identifier: GPL-2.0

obj-m += can-j1939.o

can-j1939-objs := \
        address-claim.o \
        bus.o \
        main.o \
        socket.o \
        transport.o

all:
        make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
        make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean


