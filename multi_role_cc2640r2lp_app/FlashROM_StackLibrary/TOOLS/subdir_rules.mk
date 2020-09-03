################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Each subdirectory must supply rules for building sources it contributes
build-9977473:
	@$(MAKE) --no-print-directory -Onone -f TOOLS/subdir_rules.mk build-9977473-inproc

build-9977473-inproc: ../TOOLS/app_ble.cfg
	@echo 'Building file: "$<"'
	@echo 'Invoking: XDCtools'
	"/opt/ti/ccs930/xdctools_3_60_02_34_core/xs" --xdcpath="/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source;/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/kernel/tirtos/packages;/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack;" xdc.tools.configuro -o configPkg -t ti.targets.arm.elf.M3 -p ti.platforms.simplelink:CC2640R2F -r release -c "/opt/ti/ccs930/ccs/tools/compiler/ti-cgt-arm_18.12.4.LTS" --compileOptions "-mv7M3 --code_state=16 -me -O4 --opt_for_speed=1 --include_path=\"/home/aaron/Documentos/Trabajo/ccs-workspace/multi_role_cc2640r2lp_app\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/controller/cc26xx_r2/inc\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/inc\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/rom\" --include_path=\"/home/aaron/Documentos/Trabajo/ccs-workspace/multi_role_cc2640r2lp_app/Application\" --include_path=\"/home/aaron/Documentos/Trabajo/ccs-workspace/multi_role_cc2640r2lp_app/Startup\" --include_path=\"/home/aaron/Documentos/Trabajo/ccs-workspace/multi_role_cc2640r2lp_app/PROFILES\" --include_path=\"/home/aaron/Documentos/Trabajo/ccs-workspace/multi_role_cc2640r2lp_app/Include\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/common/cc26xx\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/icall/inc\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/profiles/dev_info\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/target\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/hal/src/target/_common\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/hal/src/target/_common/cc26xx\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/hal/src/inc\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/heapmgr\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/icall/src/inc\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/osal/src/inc\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/services/src/saddr\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack/services/src/sdata\" --include_path=\"/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/devices/cc26x0r2\" --include_path=\"/opt/ti/ccs930/ccs/tools/compiler/ti-cgt-arm_18.12.4.LTS/include\" --define=DeviceFamily_CC26X0R2 --define=BOARD_DISPLAY_USE_LCD=0 --define=BOARD_DISPLAY_USE_UART=1 --define=BOARD_DISPLAY_USE_UART_ANSI=1 --define=CC2640R2_LAUNCHXL --define=CC26XX --define=CC26XX_R2 --define=ICALL_EVENTS --define=ICALL_JT --define=ICALL_LITE --define=ICALL_MAX_NUM_ENTITIES=6 --define=ICALL_MAX_NUM_TASKS=3 --define=ICALL_STACK0_ADDR --define=MAX_NUM_BLE_CONNS=3 --define=POWER_SAVING --define=STACK_LIBRARY --define=TBM_ACTIVE_ITEMS_ONLY --define=USE_ICALL --define=xdc_runtime_Assert_DISABLE_ALL --define=xdc_runtime_Log_DISABLE_ALL -g --c99 --gcc --diag_warning=225 --diag_wrap=off --display_error_number --gen_func_subsections=on --abi=eabi " "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

configPkg/linker.cmd: build-9977473 ../TOOLS/app_ble.cfg
configPkg/compiler.opt: build-9977473
configPkg/: build-9977473

