################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Each subdirectory must supply rules for building sources it contributes
TOOLS/onboard.obj: /home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/common/cc26xx/onboard.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: ARM Compiler'
	"/opt/ti/ccs930/ccs/tools/compiler/ti-cgt-arm_18.12.4.LTS/bin/armcl" --cmd_file="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/config/build_components.opt" --cmd_file="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/config/factory_config.opt" --cmd_file="/home/aaron/Documentos/Trabajo/ccs-workspace/simple_observer_cc2640r2lp_stack_library/TOOLS/build_config.opt"  -mv7M3 --code_state=16 -me -O4 --opt_for_speed=0 --include_path="/home/aaron/Documentos/Trabajo/ccs-workspace/simple_observer_cc2640r2lp_stack_library" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/controller/cc26xx_r2/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/rom" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/common/cc26xx" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/common/cc26xx/npi/stack" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/examples/rtos/CC2640R2_LAUNCHXL/blestack/simple_observer/src/stack" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/icall/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/profiles/roles" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/hal/src/target/_common" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/hal/src/target/_common/cc26xx" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/hal/src/target" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/hal/src/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/icall/src/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/npi/src" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/osal/src/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/services/src/aes/cc26xx" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/services/src/nv/cc26xx" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/services/src/nv" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/services/src/saddr" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/devices/cc26x0r2" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/devices/cc26x0r2/rf_patches" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/devices/cc26x0r2/inc" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source" --include_path="/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/kernel/tirtos/packages" --include_path="/opt/ti/ccs930/xdctools_3_60_02_34_core/packages" --include_path="/opt/ti/ccs930/ccs/tools/compiler/ti-cgt-arm_18.12.4.LTS/include" --define=CC26XX --define=CC26XX_R2 --define=DeviceFamily_CC26X0R2 --define=EXT_HAL_ASSERT --define=FLASH_ROM_BUILD --define=ICALL_EVENTS --define=ICALL_JT --define=ICALL_LITE --define=OSAL_CBTIMER_NUM_TASKS=1 --define=OSAL_SNV=1 --define=POWER_SAVING --define=STACK_LIBRARY --define=USE_ICALL -g --c99 --gcc --diag_warning=225 --diag_wrap=off --display_error_number --gen_func_subsections=on --abi=eabi --preproc_with_compile --preproc_dependency="TOOLS/$(basename $(<F)).d_raw" --obj_directory="TOOLS" $(GEN_OPTS__FLAG) "$(shell echo $<)"
	@echo 'Finished building: "$<"'
	@echo ' '


