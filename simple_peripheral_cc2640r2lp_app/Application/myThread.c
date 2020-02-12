#include <xdc/std.h>
#include <xdc/runtime/Error.h>
#include <ti/sysbios/knl/Task.h>
#include <ti/display/Display.h>
#include <stdlib.h>
#include <unistd.h>
#include "myThread.h"
#include "VL6180X_Service.h"
#include "vl6180x_includes.h"
#include "vl6180x_platform.h"



#define THREADSTACKSIZE    1024

#define VL6180X_ADDR        0x29;

Display_Handle display = NULL;
int32_t data;


Task_Struct myTask;
uint8_t myTaskStack[THREADSTACKSIZE];



int myUsleep(useconds_t usec)
{
    UInt32 timeout;

    /* usec must be less than 1000000 */
    if (usec >= 1000000) {
        errno = EINVAL;
        return (-1);
    }

    /*  Implementations may place limitations on the granularity of timer
     *  values. For each interval timer, if the requested timer value requires
     *  a finer granularity than the implementation supports, the actual timer
     *  value shall be rounded up to the next supported value.
     */
    /* Clock_tickPeriod is the Clock period in microseconds */
    timeout = (UInt32)((usec + Clock_tickPeriod - 1) / Clock_tickPeriod);

    /* must add one tick to ensure a full duration of timeout ticks */
    Task_sleep(timeout + 1);

    return (0);
}

void MyDev_ShowRange (VL6180xDev_t dev, int32_t range_mm, int status){
    Display_printf(display,0,0,"distance: %i mm",range_mm);
}

void MyDev_ShowErr(VL6180xDev_t dev, uint32_t errorStatus){
    Display_printf(display,0,0,"ERROR! # %i",errorStatus);
}

void Sample_SimpleRanging(void) {

            struct MyVL6180Dev_t st = {0};
            VL6180xDev_t myDev = &st;
            myDev->slave_addr = 0x29;

            VL6180x_InitData(myDev);
            //Esta funcion nos permite duplicar o triplicar el alcance inicial (200 mm) aunque a costa de perder precision
            VL6180x_UpscaleSetScaling(myDev, 3);
            VL6180x_Prepare(myDev);

            VL6180x_RangeData_t Range;

            do {
                VL6180x_RangePollMeasurement(myDev, &Range);
                if (Range.errorStatus == NoError){
                    MyDev_ShowRange(myDev, Range.range_mm, 0); // your code display range in mm
                    data = Range.range_mm;
                    //VL6180X_Service_SetParameter(VL6180X_SERVICE_DISTANCE_ID, VL6180X_SERVICE_DISTANCE_LEN, &data);
                }
                else {
                    MyDev_ShowErr(myDev, Range.errorStatus); // your code display error code
                }
               myUsleep(50000); //50 ms
            } while (1); // your code to stop looping

}

static void myThread(UArg a0, UArg a1) {

    display = Display_open(Display_Type_UART, NULL);
    if (display == NULL) {
        while (1);
    }
    Sample_SimpleRanging();
    //return 0;
    return;
}

void VL6180X_Thread_create(void) {
  Task_Params taskParams;

  /* Configure task */
  Task_Params_init(&taskParams);
  taskParams.stack = myTaskStack;
  taskParams.stackSize = THREADSTACKSIZE;
  taskParams.priority = 1;

  Task_construct(&myTask, myThread, &taskParams, Error_IGNORE);
}
