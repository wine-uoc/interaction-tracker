/*
 * vl6180x_platform.c
 *
 *  Created on: 21 ago. 2019
 *      Author: aaron
 */

#include <vl6180x_platform.h>
#include "myThread.h"

void VL6180x_PollDelay(VL6180xDev_t dev){
    //Delay 5 ms
    myUsleep(5000);
}


