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

#include <ti/sysbios/knl/Task.h>
#include <ti/sysbios/knl/Clock.h>
#include <ti/sysbios/knl/Event.h>
#include <ti/sysbios/knl/Queue.h>
#include <ti/display/Display.h>
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
#define DEFAULT_SCAN_DURATION                 4000

// Discovery mode (limited, general, all)
#define DEFAULT_DISCOVERY_MODE                DEVDISC_MODE_ALL

// TRUE to use active scan
#define DEFAULT_DISCOVERY_ACTIVE_SCAN         FALSE

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
#define SBO_TASK_STACK_SIZE                   660
#endif

#define SBO_STATE_CHANGE_EVT                  0x0001
#define SBO_KEY_CHANGE_EVT                    0x0002

// Internal Events for RTOS application
#define SBO_ICALL_EVT                         ICALL_MSG_EVENT_ID // Event_Id_31
#define SBO_QUEUE_EVT                         UTIL_QUEUE_EVENT_ID // Event_Id_30

#define SBO_ALL_EVENTS                        (SBO_ICALL_EVT | SBO_QUEUE_EVT)

/*********************************************************************
 * TYPEDEFS
 */

// App event passed from profiles.
typedef struct
{
  appEvtHdr_t hdr; // event header
  uint8_t *pData;  // event data
} sboEvt_t;

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
 */

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

// Scan result list
static gapDevRec_t devList[DEFAULT_MAX_SCAN_RES];

// Scanning state
static uint8 scanning = FALSE;

/*********************************************************************
 * LOCAL FUNCTIONS
 */
static void SimpleObserver_init(void);
static void SimpleObserver_taskFxn(UArg a0, UArg a1);

static void SimpleObserver_handleKeys(uint8_t shift, uint8_t keys);
static void SimpleObserver_processStackMsg(ICall_Hdr *pMsg);
static void SimpleObserver_processAppMsg(sboEvt_t *pMsg);
static void SimpleObserver_processRoleEvent(gapObserverRoleEvent_t *pEvent);
static void SimpleObserver_addDeviceInfo(uint8 *pAddr, uint8 addrType);

static uint8_t SimpleObserver_eventCB(gapObserverRoleEvent_t *pEvent);

static uint8_t SimpleObserver_enqueueMsg(uint8_t event, uint8_t status,
                                            uint8_t *pData);

void SimpleObserver_initKeys(void);

void SimpleObserver_keyChangeHandler(uint8 keys);

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

  Board_initKeys(SimpleObserver_keyChangeHandler);

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

    case SBO_KEY_CHANGE_EVT:
      SimpleObserver_handleKeys(0, pMsg->hdr.state);
      break;

    default:
      // Do nothing.
      break;
  }
}

/*********************************************************************
 * @fn      SimpleObserver_handleKeys
 *
 * @brief   Handles all key events for this device.
 *
 * @param   shift - true if in shift/alt.
 * @param   keys - bit field for key events. Valid entries:
 *                 HAL_KEY_SW_2
 *                 HAL_KEY_SW_1
 *
 * @return  none
 */
static void SimpleObserver_handleKeys(uint8 shift, uint8 keys)
{
  (void)shift;  // Intentionally unreferenced parameter

  // Left key determines action to take
  if (keys & KEY_LEFT)
  {
    if (!scanning)
    {
      // Increment index
      scanIdx++;

        if (scanIdx >= scanRes)
        {
          // Prompt the user to begin scanning again.
          scanIdx = -1;
          Display_print0(dispHandle, 2, 0, "");
          Display_print0(dispHandle, 3, 0, "");
          Display_print0(dispHandle, 5, 0, "Discover ->");
        }
        else
        {
          // Display the indexed scanned device.
          Display_print1(dispHandle, 2, 0, "Device %d", (scanIdx + 1));
          Display_print0(dispHandle, 3, 0, Util_convertBdAddr2Str(devList[scanIdx].addr));
          Display_print0(dispHandle, 5, 0, "");
          Display_print0(dispHandle, 6, 0, "<- Next Option");
        }
    }
  }

  // Right key takes the actio the user has selected.
  if (keys & KEY_RIGHT)
  {
    if (scanIdx == -1)
    {
      if (!scanning)
      {
        scanning = TRUE;
        scanRes = 0;

        Display_print0(dispHandle, 2, 0, "Discovering...");
        Display_print0(dispHandle, 3, 0, "");
        Display_print0(dispHandle, 4, 0, "");
        Display_print0(dispHandle, 5, 0, "Cancel Discovery ->");
        Display_print0(dispHandle, 6, 0, "");

        GAPObserverRole_StartDiscovery(DEFAULT_DISCOVERY_MODE,
                                       DEFAULT_DISCOVERY_ACTIVE_SCAN,
                                       DEFAULT_DISCOVERY_WHITE_LIST);
      }
      else
      {
        // Cancel Scanning
        GAPObserverRole_CancelDiscovery();
      }
    }
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
        Display_print0(dispHandle, 1, 0, Util_convertBdAddr2Str(pEvent->initDone.devAddr));
        Display_print0(dispHandle, 2, 0, "Initialized");

        // Prompt user to begin scanning.
        Display_print0(dispHandle, 5, 0, "Discover ->");
      }
      break;

    case GAP_DEVICE_INFO_EVENT:
      {
        SimpleObserver_addDeviceInfo(pEvent->deviceInfo.addr,
                                        pEvent->deviceInfo.addrType);
      }
      break;

    case GAP_DEVICE_DISCOVERY_EVENT:
      {
        if(pEvent->gap.hdr.status == SUCCESS)
        {
            // Discovery complete.
            scanning = FALSE;

            if(ENABLE_UNLIMITED_SCAN_RES == FALSE)
            {
                // Copy results.
                scanRes = pEvent->discCmpl.numDevs;
                memcpy(devList, pEvent->discCmpl.pDevList,
                   (sizeof(gapDevRec_t) * pEvent->discCmpl.numDevs));
            }

            Display_print1(dispHandle, 2, 0, "Devices Found %d", scanRes);

            if ( scanRes > 0 )
            {
              Display_print0(dispHandle, 3, 0, "<- To Select");
            }

            // Initialize scan index.
            scanIdx = -1;

            // Prompt user that re-performing scanning at this state is possible.
            Display_print0(dispHandle, 5, 0, "Discover ->");
        }
        else
        {
            if(pEvent->gap.hdr.status == GAP_LLERROR_INVALID_PARAMETERS)
            {
                Display_print0(dispHandle, 3, 0, "INVALID PARAMETERS");
            }
            else if(pEvent->gap.hdr.status == GAP_LLERROR_COMMAND_DISALLOWED)
            {
                Display_print0(dispHandle, 3, 0, "COMMAND DISALLOWED");
            }
            else
            {
                Display_print0(dispHandle, 3, 0, "ERROR");
            }
        }
      }
      break;

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
 * @fn      SimpleObserver_keyChangeHandler
 *
 * @brief   Key event handler function
 *
 * @param   keys pressed
 *
 * @return  none
 */
void SimpleObserver_keyChangeHandler(uint8 keys)
{
  SimpleObserver_enqueueMsg(SBO_KEY_CHANGE_EVT, keys, NULL);
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

/*********************************************************************
*********************************************************************/
