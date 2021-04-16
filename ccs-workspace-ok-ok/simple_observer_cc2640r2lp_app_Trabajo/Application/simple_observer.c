/******************************************************************************

 @file  simple_observer.c

 @brief This file contains the Simple Observer sample application for use
        with the CC2650 Bluetooth Low Energy Protocol Stack.

 Group: WCS, BTS
 Target Device: cc2640r2

 ******************************************************************************
 
 Copyright (c) 2011-2020, Texas Instruments Incorporated
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:

 *  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

 *  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

 *  Neither the name of Texas Instruments Incorporated nor the names of
    its contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 ******************************************************************************
 
 
 *****************************************************************************/

/*********************************************************************
 * INCLUDES
 */
#include <string.h>
#include <stdio.h>
#include <xdc/runtime/System.h>

#include <ti/sysbios/knl/Task.h>
#include <ti/sysbios/knl/Clock.h>
#include <ti/sysbios/knl/Event.h>
#include <ti/sysbios/knl/Queue.h>
#include <ti/display/Display.h>
#include <inc/hw_fcfg1.h>
#include <icall.h>
#include "util.h"
/* This Header file contains all BLE API and icall structure definition */
#include "icall_ble_api.h"

#include "observer.h"
#include "board_key.h"
#include "board.h"

#include "simple_observer.h"

/*********************************************************************
 * MACROS
 */

/*********************************************************************
 * CONSTANTS
 */

// Enable/Disable Unlimited Scanning Feature
#define ENABLE_UNLIMITED_SCAN_RES             FALSE

// Maximum number of scan responses
#define DEFAULT_MAX_SCAN_RES                  8

// Scan duration in ms
#define DEFAULT_SCAN_DURATION                 100

//Maximum device name length
#define DEV_NAME_MAX_STR_LEN                  16


#define MAC_ADDRESS_LEN                       6

// Discovery mode (limited, general, all)
#define DEFAULT_DISCOVERY_MODE                DEVDISC_MODE_ALL

// TRUE to use active scan
#define DEFAULT_DISCOVERY_ACTIVE_SCAN         TRUE

// Set desired policy to use during discovery (use values from GAP_Disc_Filter_Policies)
#define DEFAULT_DISCOVERY_WHITE_LIST          GAP_DISC_FILTER_POLICY_ALL

// Type of Display to open
#if !defined(Display_DISABLE_ALL)
  #if defined(BOARD_DISPLAY_USE_LCD) && (BOARD_DISPLAY_USE_LCD!=0)
    #define SBO_DISPLAY_TYPE Display_Type_LCD
  #elif defined (BOARD_DISPLAY_USE_UART) && (BOARD_DISPLAY_USE_UART!=0)
    #define SBO_DISPLAY_TYPE Display_Type_UART
  #else // !BOARD_DISPLAY_USE_LCD && !BOARD_DISPLAY_USE_UART
    #define SBO_DISPLAY_TYPE 0 // Option not supported
  #endif // BOARD_DISPLAY_USE_LCD && BOARD_DISPLAY_USE_UART
#else // BOARD_DISPLAY_USE_LCD && BOARD_DISPLAY_USE_UART
  #define SBO_DISPLAY_TYPE 0 // No Display
#endif // Display_DISABLE_ALL

// Task configuration
#define SBO_TASK_PRIORITY                     1

#ifndef SBO_TASK_STACK_SIZE
#define SBO_TASK_STACK_SIZE                   4096
#endif

#define SBO_STATE_CHANGE_EVT                  0x0001
#define SBO_KEY_CHANGE_EVT                    0x0002

// Internal Events for RTOS application
#define SBO_ICALL_EVT                         ICALL_MSG_EVENT_ID // Event_Id_31
#define SBO_QUEUE_EVT                         UTIL_QUEUE_EVENT_ID // Event_Id_30
#define SBO_PERIODIC_EVT                      Event_Id_06
#define SBO_ALL_EVENTS                        (SBO_ICALL_EVT | SBO_QUEUE_EVT | SBO_PERIODIC_EVT)

/*********************************************************************
 * TYPEDEFS
 */

// App event passed from profiles.
typedef struct
{
  appEvtHdr_t hdr; // event header
  uint8_t *pData;  // event data
} sboEvt_t;

typedef struct
{
  uint8 addr [MAC_ADDRESS_LEN];
  char devName [DEV_NAME_MAX_STR_LEN];
  int8 rssi;
} devnameRSSIinfo;

/*********************
/*********************************************************************
 * GLOBAL VARIABLES
 */

// Display Interface
Display_Handle dispHandle = NULL;

/*********************************************************************
 * EXTERNAL VARIABLES
 */

/*********************************************************************
 * EXTERNAL FUNCTIONS
 */

/*********************************************************************
 * LOCAL VARIABLES
 *
 */

static devnameRSSIinfo tupleInfo[DEFAULT_MAX_SCAN_RES];

// Entity ID globally used to check for source and/or destination of messages
static ICall_EntityID selfEntity;

static ICall_SyncHandle syncEvent;

// Clock object used to signal timeout
static Clock_Struct keyChangeClock;

// Queue object used for app messages
static Queue_Struct appMsg;
static Queue_Handle appMsgQueue;

// Task configuration
Task_Struct sboTask;
Char sboTaskStack[SBO_TASK_STACK_SIZE];

// Number of scan results and scan result index
static uint8 scanRes = 0 ;
static int8 scanIdx = -1;
static uint8_t scanDevices = 0;
// Scan result list
static gapDevRec_t devList[DEFAULT_MAX_SCAN_RES];

// Scanning state
static uint8 scanning = FALSE;

static uint32_t line_pr = 0;
/*********************************************************************
 * LOCAL FUNCTIONS
 */
static void SimpleObserver_init(void);
static void SimpleObserver_taskFxn(UArg a0, UArg a1);

static void SimpleObserver_processStackMsg(ICall_Hdr *pMsg);
static void SimpleObserver_processAppMsg(sboEvt_t *pMsg);
static void SimpleObserver_processRoleEvent(gapObserverRoleEvent_t *pEvent);
static void SimpleObserver_addDeviceInfo(uint8 *pAddr, uint8 addrType);
int isValidDevice(gapDeviceInfoEvent_t *devInfo, char* devname, uint8_t* dataLen);

static uint8_t SimpleObserver_eventCB(gapObserverRoleEvent_t *pEvent);

static uint8_t SimpleObserver_enqueueMsg(uint8_t event, uint8_t status,
                                            uint8_t *pData);
static void addAddrDeviceRssiInfo (char *devname, uint8_t data_len, int8 rssi, uint8* addr);
void SimpleObserver_initKeys(void);
//void SimpleObserver_keyChangeHandler(uint8 keys);
void printScannedDevicesInfo();
/*********************************************************************
 * PROFILE CALLBACKS
 */

// GAP Role Callbacks
static const gapObserverRoleCB_t simpleRoleCB =
{
  SimpleObserver_eventCB  // Event callback
};

/*********************************************************************
 * PUBLIC FUNCTIONS
 */

/*********************************************************************
 * @fn      SimpleObserver_createTask
 *
 * @brief   Task creation function for the Simple Observer.
 *
 * @param   none
 *
 * @return  none
 */
void SimpleObserver_createTask(void)
{
  Task_Params taskParams;

  // Configure task
  Task_Params_init(&taskParams);
  taskParams.stack = sboTaskStack;
  taskParams.stackSize = SBO_TASK_STACK_SIZE;
  taskParams.priority = SBO_TASK_PRIORITY;

  Task_construct(&sboTask, SimpleObserver_taskFxn, &taskParams, NULL);
}

/*********************************************************************
 * @fn      SimpleObserver_init
 *
 * @brief   Initialization function for the Simple Observer App Task.
 *          This is called during initialization and should contain
 *          any application specific initialization (ie. hardware
 *          initialization/setup, table initialization, power up
 *          notification).
 *
 * @param   none
 *
 * @return  none
 */
void SimpleObserver_init(void)
{
  // ******************************************************************
  // NO STACK API CALLS CAN OCCUR BEFORE THIS CALL TO ICall_registerApp
  // ******************************************************************
  // Register the current thread as an ICall dispatcher application
  // so that the application can send and receive messages.
  ICall_registerApp(&selfEntity, &syncEvent);

  // Hard code the DB Address till CC2650 board gets its own IEEE address
  //uint8 bdAddress[B_ADDR_LEN] = { 0x44, 0x44, 0x44, 0x44, 0x44, 0x44 };
  //HCI_EXT_SetBDADDRCmd(bdAddress);

  // Create an RTOS queue for message from profile to be sent to app.
  appMsgQueue = Util_constructQueue(&appMsg);

  //Board_initKeys(SimpleObserver_keyChangeHandler);

  dispHandle = Display_open(SBO_DISPLAY_TYPE, NULL);

  // Setup Observer Profile
  {
      uint8_t scanRes = 0;

      // In case that the Unlimited Scanning feature is disabled
      // send the number of scan results to the GAP
      if(ENABLE_UNLIMITED_SCAN_RES == FALSE)
      {
          scanRes = DEFAULT_MAX_SCAN_RES;
      }

    GAPObserverRole_SetParameter(GAPOBSERVERROLE_MAX_SCAN_RES, sizeof(uint8_t),
                                 &scanRes );
  }

  // Setup GAP
  GAP_SetParamValue(TGAP_GEN_DISC_SCAN, DEFAULT_SCAN_DURATION);
  GAP_SetParamValue(TGAP_LIM_DISC_SCAN, DEFAULT_SCAN_DURATION);

  // Start the Device
  VOID GAPObserverRole_StartDevice((gapObserverRoleCB_t *)&simpleRoleCB);

  Display_print0(dispHandle, 0, 0, "BLE Observer");
}

/*********************************************************************
 * @fn      SimpleObserver_taskFxn
 *
 * @brief   Application task entry point for the Simple Observer.
 *
 * @param   none
 *
 * @return  none
 */
static void SimpleObserver_taskFxn(UArg a0, UArg a1)
{
  // Initialize application
  SimpleObserver_init();
  GAPObserverRole_StartDiscovery(DEFAULT_DISCOVERY_MODE,
                                       DEFAULT_DISCOVERY_ACTIVE_SCAN,
                                       DEFAULT_DISCOVERY_WHITE_LIST);
  // Application main loop
  for (;;)
  {
    uint32_t events;

    events = Event_pend(syncEvent, Event_Id_NONE, SBO_ALL_EVENTS,
                        ICALL_TIMEOUT_FOREVER);

    if (events)
    {
      ICall_EntityID dest;
      ICall_ServiceEnum src;
      ICall_HciExtEvt *pMsg = NULL;

      if (ICall_fetchServiceMsg(&src, &dest,
                                (void **)&pMsg) == ICALL_ERRNO_SUCCESS)
      {
        if ((src == ICALL_SERVICE_CLASS_BLE) && (dest == selfEntity))
        {
          // Process inter-task message
          SimpleObserver_processStackMsg((ICall_Hdr *)pMsg);
        }

        if (pMsg)
        {
          ICall_freeMsg(pMsg);
        }
      }
    }

    // If RTOS queue is not empty, process app message
    if (events & SBO_QUEUE_EVT)
    {
      while (!Queue_empty(appMsgQueue))
      {
        sboEvt_t *pMsg = (sboEvt_t *)Util_dequeueMsg(appMsgQueue);
        if (pMsg)
        {
          // Process message
          SimpleObserver_processAppMsg(pMsg);

          // Free the space from the message
          ICall_free(pMsg);
        }
      }
    }
  }
}

/*********************************************************************
 * @fn      SimpleObserver_processStackMsg
 *
 * @brief   Process an incoming task message.
 *
 * @param   pMsg - message to process
 *
 * @return  none
 */
static void SimpleObserver_processStackMsg(ICall_Hdr *pMsg)
{
  switch (pMsg->event)
  {
    case GAP_MSG_EVENT:
      SimpleObserver_processRoleEvent((gapObserverRoleEvent_t *)pMsg);
      break;

    default:
      break;
  }
}

/*********************************************************************
 * @fn      SimpleObserver_processAppMsg
 *
 * @brief   Central application event processing function.
 *
 * @param   pMsg - pointer to event structure
 *
 * @return  none
 */
static void SimpleObserver_processAppMsg(sboEvt_t *pMsg)
{
  switch (pMsg->hdr.event)
  {
    case SBO_STATE_CHANGE_EVT:
      SimpleObserver_processStackMsg((ICall_Hdr *)pMsg->pData);

      // Free the stack message
      ICall_freeMsg(pMsg->pData);
      break;

    default:
      // Do nothing.
      break;
  }
}


/*********************************************************************
 * @fn      SimpleObserver_processRoleEvent
 *
 * @brief   Observer role event processing function.
 *
 * @param   pEvent - pointer to event structure
 *
 * @return  none
 */
static void SimpleObserver_processRoleEvent(gapObserverRoleEvent_t *pEvent)
{
  switch ( pEvent->gap.opcode )
  {
    case GAP_DEVICE_INIT_DONE_EVENT:
      {
          Display_clear(dispHandle);
      }
      break;

    case GAP_DEVICE_INFO_EVENT:
      {
      // Display_print0(dispHandle,6,0,"Device discovered!");
        if(ENABLE_UNLIMITED_SCAN_RES == TRUE)
        {
            SimpleObserver_addDeviceInfo(pEvent->deviceInfo.addr, pEvent->deviceInfo.addrType);
        }
        if(pEvent->deviceInfo.eventType == GAP_ADRPT_SCAN_RSP)
        {

        }
        else {
           char* devname = calloc(16, sizeof(char));
           uint8* macAddr = calloc(MAC_ADDRESS_LEN, sizeof(uint8));
           uint8 dataLen;
           if (isValidDevice(&pEvent->deviceInfo, devname, &dataLen)){
              memcpy(macAddr, pEvent->deviceInfo.addr, MAC_ADDRESS_LEN);
              addAddrDeviceRssiInfo(devname, dataLen, pEvent->deviceInfo.rssi, macAddr);
              memset(pEvent->deviceInfo.pEvtData, 0, pEvent->deviceInfo.dataLen);
           }
           free(devname);
           free(macAddr);
        }
      }
      break;

    case GAP_DEVICE_DISCOVERY_EVENT:
      {
          printScannedDevicesInfo();
          GAPObserverRole_StartDiscovery(DEFAULT_DISCOVERY_MODE,
                                           DEFAULT_DISCOVERY_ACTIVE_SCAN,
                                           DEFAULT_DISCOVERY_WHITE_LIST);
      }
    default:
      break;
  }
}

/*********************************************************************
 * @fn      SimpleObserver_eventCB
 *
 * @brief   Observer event callback function.
 *
 * @param   pEvent - pointer to event structure
 *
 * @return  TRUE if safe to deallocate event message, FALSE otherwise.
 */
static uint8_t SimpleObserver_eventCB(gapObserverRoleEvent_t *pEvent)
{
  // Forward the role event to the application
  if (SimpleObserver_enqueueMsg(SBO_STATE_CHANGE_EVT,
                                   SUCCESS, (uint8_t *)pEvent))
  {
    // App will process and free the event
    return FALSE;
  }

  // Caller should free the event
  return TRUE;
}

/*********************************************************************
 * @fn      SimpleObserver_addDeviceInfo
 *
 * @brief   Add a device to the device discovery result list
 *
 * @return  none
 */
static void SimpleObserver_addDeviceInfo(uint8 *pAddr, uint8 addrType)
{
  uint8 i;

  // If result count not at max
  if ( scanRes < DEFAULT_MAX_SCAN_RES )
  {
    // Check if device is already in scan results
    for ( i = 0; i < scanRes; i++ )
    {
      if (memcmp(pAddr, devList[i].addr, B_ADDR_LEN) == 0)
      {
        return;
      }
    }
    // Add addr to scan result list
    memcpy(devList[scanRes].addr, pAddr, B_ADDR_LEN );
    devList[scanRes].addrType = addrType;

    // Increment scan result count
    scanRes++;
  }
}


/*********************************************************************
 * @fn      SimpleObserver_enqueueMsg
 *
 * @brief   Creates a message and puts the message in RTOS queue.
 *
 * @param   event - message event.
 * @param   state - message state.
 * @param   pData - message data pointer.
 *
 * @return  TRUE or FALSE
 */
static uint8_t SimpleObserver_enqueueMsg(uint8_t event, uint8_t state,
                                           uint8_t *pData)
{
  sboEvt_t *pMsg;

  // Create dynamic pointer to message.
  if (pMsg = ICall_malloc(sizeof(sboEvt_t)))
  {
    pMsg->hdr.event = event;
    pMsg->hdr.state = state;
    pMsg->pData = pData;

    // Enqueue the message.
    return Util_enqueueMsg(appMsgQueue, syncEvent, (uint8_t *)pMsg);
  }

  return FALSE;
}

void printScannedDevicesInfo(){

   //Display_clear(dispHandle);

   int i = 0;
   //int line_pr = 0;

   uint32_t anchorMAC_LO;
   uint16_t anchorMAC_HI;

   anchorMAC_HI = *((uint16_t *)(FCFG1_BASE + FCFG1_O_MAC_BLE_1)) & 0xFFFF;
   anchorMAC_LO = *((uint32_t *)(FCFG1_BASE + FCFG1_O_MAC_BLE_0)) & 0xFFFFFFFF;

   char anchorMAC_str [13];

   sprintf(anchorMAC_str, "%02x%02x%02x%02x%02x%02x", anchorMAC_HI >> 8, anchorMAC_HI & 0x00FF,
                                                      anchorMAC_LO >> 24, (anchorMAC_LO >> 16) & 0x000000FF,
                                                      (anchorMAC_LO >> 8) & 0x000000FF, anchorMAC_LO & 0x000000FF);


   for (i = 0; i < scanDevices; ++i){
       Display_clear(dispHandle);

       uint32_t beaconMAC_LO;
       uint16_t beaconMAC_HI;

       char devname[16];

       memset(devname, '\0', 16);
       memcpy(devname, tupleInfo[i].devName, 16);

       memset(&beaconMAC_LO, '\0', sizeof(uint32_t));
       memcpy(&beaconMAC_LO, tupleInfo[i].addr, 4);

       memset(&beaconMAC_HI, '\0', sizeof(uint16_t));
       memcpy(&beaconMAC_HI, &tupleInfo[i].addr[4], 2);


      //Display the anchorMAC, beaconId (TARGETDEV-...), beaconMAC and RSSI
      Display_print5(dispHandle, line_pr , 0 ,"%s %s %02x%02x %d \n", anchorMAC_str, devname, beaconMAC_HI, beaconMAC_LO, tupleInfo[i].rssi);

   }

   memset(tupleInfo, '\0', sizeof(devnameRSSIinfo)*scanDevices);
   scanRes = 0;
   scanDevices = 0;

}

static void SimpleObserver_clockHandler(UArg arg){

    //Wake up the application.
    Event_post(syncEvent, arg);
}

static void addAddrDeviceRssiInfo (char *devname, uint8_t data_len, int8 rssi, uint8 *addr){
      uint8_t i;

      //If found device is the target device

      // If result count not at max
      if (scanDevices < DEFAULT_MAX_SCAN_RES)
      {
        // Check if device is already in scan results
        for (i = 0; i < scanDevices; i++)
        {
           if (memcmp(devname, tupleInfo[i].devName , data_len) == 0)
          {
             tupleInfo[i].rssi = rssi;
             return;
          }
        }

        // Add devName to scan result list
        memcpy(tupleInfo[scanDevices].devName, devname, data_len);
        tupleInfo[scanDevices].rssi = rssi;
        memcpy(tupleInfo[scanDevices].addr, addr, MAC_ADDRESS_LEN);

        // Increment scan result count
        ++scanDevices;
      }
}

/*
 * isValidDevice returns true when the detected device is either a target mobile or a launchpad.
 * Otherwise returns false.
 */
int isValidDevice(gapDeviceInfoEvent_t *devInfo, char* devname, uint8_t* dataLen){
    char *found_mob = strstr((char*) devInfo->pEvtData, "TARGETDEV-");
    char *found_anc = strstr((char*) devInfo->pEvtData, "ANC-");

    if (found_mob != 0){
        int i;
        for (i = 0; i < 16; ++i){
            devname[i] = *(found_mob+i);
        }

        *dataLen = 16;

        return 1;
    }
    else if (found_anc != 0){

        int i;
        for (i = 0; i < 8; ++i){
            devname[i] = *(found_anc+i);
        }

        *dataLen = 8;

        return 1;
    }
    else return 0;
}
/*********************************************************************
*********************************************************************/
