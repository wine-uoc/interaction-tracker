/*
 * myThread.h
 *
 *  Created on: 30 sept. 2019
 *      Author: aaron
 */

#ifndef APPLICATION_MYTHREAD_H_
#define APPLICATION_MYTHREAD_H_

#include <errno.h>
#include <time.h>
#include <stdint.h>
#include <unistd.h>

#include <xdc/std.h>
#include <ti/sysbios/knl/Clock.h>
#include <ti/sysbios/knl/Task.h>

extern void VL6180X_Thread_create(void);
static void myThread(UArg a0, UArg a1);

int myUsleep(useconds_t usec);

#endif /* APPLICATION_MYTHREAD_H_ */
