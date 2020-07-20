/******************************************************************************

 @file  multi_role_menu.h

 @brief This file contains macros, type definitions, and function prototypes
        for two-button menu implementation.

 Group: WCS BTS
 Target Device: cc2640r2

 ******************************************************************************
 
 Copyright (c) 2016-2020, Texas Instruments Incorporated
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

#ifndef MICRO_BLE_TEST_MENU_H
#define MICRO_BLE_TEST_MENU_H

#ifdef __cplusplus
extern "C"
{
#endif

/*
 * Menus Declarations
 */

/* Main Menu Object */
extern tbmMenuObj_t mrMenuMain;

/* Items of Main */
extern tbmMenuObj_t mrMenuScan;
extern tbmMenuObj_t mrMenuConnect;
extern tbmMenuObj_t mrMenuGattRw;
extern tbmMenuObj_t mrMenuConnUpdate;
extern tbmMenuObj_t mrMenuDisconnect;
extern tbmMenuObj_t mrMenuAdvertise;

#ifdef __cplusplus
}
#endif

#endif /* MICRO_BLE_TEST_MENU_H */

