################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Each subdirectory must supply rules for building sources it contributes
Drivers/RF/RFCC26XX_singleMode.obj: /home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/drivers/rf/RFCC26XX_singleMode.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: Arm Compiler'
	"/home/aaron/ti/ccs1020/ccs/tools/compiler/ti-cgt-arm_18.12.7.LTS/bin/armcl" --cmd_file="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/config/build_components.opt" --cmd_file="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/config/factory_config.opt" --cmd_file="/home/aaron/Trabajo/interaction-tracker-updated/ccs-workspace-ok-ok/simple_observer_cc2640r2lp_stack_library_Trabajo/TOOLS/build_config.opt"  -mv7M3 --code_state=16 -me -O4 --opt_for_speed=0 --include_path="/home/aaron/Trabajo/interaction-tracker-updated/ccs-workspace-ok-ok/simple_observer_cc2640r2lp_app_Trabajo" --include_path="/home/aaron/Trabajo/interaction-tracker-updated/ccs-workspace-ok-ok/simple_observer_cc2640r2lp_app_Trabajo/Application" --include_path="/home/aaron/Trabajo/interaction-tracker-updated/ccs-workspace-ok-ok/simple_observer_cc2640r2lp_app_Trabajo/Startup" --include_path="/home/aaron/Trabajo/interaction-tracker-updated/ccs-workspace-ok-ok/simple_observer_cc2640r2lp_app_Trabajo/PROFILES" --include_path="/home/aaron/Trabajo/interaction-tracker-updated/ccs-workspace-ok-ok/simple_observer_cc2640r2lp_app_Trabajo/Include" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/controller/cc26xx_r2/inc" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/inc" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/rom" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/examples/rtos/CC2640R2_LAUNCHXL/blestack/simple_observer/src/app" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/icall/inc" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/profiles/roles/cc26xx" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/profiles/roles" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/common/cc26xx" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/target" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/hal/src/target/_common" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/hal/src/target/_common/cc26xx" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/hal/src/inc" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/heapmgr" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/icall/src/inc" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/osal/src/inc" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/services/src/saddr" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack/services/src/sdata" --include_path="/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/devices/cc26x0r2" --include_path="/home/aaron/ti/ccs1020/ccs/tools/compiler/ti-cgt-arm_18.12.7.LTS/include" --define=DeviceFamily_CC26X0R2 --define=BOARD_DISPLAY_USE_LCD=0 --define=BOARD_DISPLAY_USE_UART=1 --define=BOARD_DISPLAY_USE_UART_ANSI=1 --define=CC2640R2_LAUNCHXL --define=CC26XX --define=CC26XX_R2 --define=ICALL_EVENTS --define=ICALL_JT --define=ICALL_LITE --define=ICALL_MAX_NUM_ENTITIES=6 --define=ICALL_MAX_NUM_TASKS=3 --define=ICALL_STACK0_ADDR --define=POWER_SAVING --define=STACK_LIBRARY --define=USE_ICALL --define=xdc_runtime_Assert_DISABLE_ALL --define=xdc_runtime_Log_DISABLE_ALL -g --c99 --gcc --diag_warning=225 --diag_wrap=off --display_error_number --gen_func_subsections=on --abi=eabi --preproc_with_compile --preproc_dependency="Drivers/RF/$(basename $(<F)).d_raw" --obj_directory="Drivers/RF" $(GEN_OPTS__FLAG) "$(shell echo $<)"
	@echo 'Finished building: "$<"'
	@echo ' '


