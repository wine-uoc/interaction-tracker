################################################################################
# Automatically-generated file. Do not edit!
################################################################################

CG_TOOL_ROOT := /opt/ti/ccs930/ccs/tools/compiler/ti-cgt-arm_18.12.4.LTS

GEN_OPTS__FLAG := 
GEN_CMDS__FLAG := 

ORDERED_OBJS += \
"./HAL/Common/hal_assert.obj" \
"./HAL/Target/CC2650/Drivers/hal_flash_wrapper.obj" \
"./HAL/Target/CC2650/Drivers/hal_rtc_wrapper.obj" \
"./HAL/Target/CC2650/Drivers/hal_trng_wrapper.obj" \
"./HAL/Target/CC2650/_common/mb_patch.obj" \
"./Host/gatt_uuid.obj" \
"./ICallBLE/ble_dispatch_JT.obj" \
"./ICallBLE/ble_dispatch_lite.obj" \
"./ICallBLE/icall_lite_translation.obj" \
"./NPI/npi.obj" \
"./OSAL/osal.obj" \
"./OSAL/osal_bufmgr.obj" \
"./OSAL/osal_cbtimer.obj" \
"./OSAL/osal_clock.obj" \
"./OSAL/osal_memory_icall.obj" \
"./OSAL/osal_pwrmgr.obj" \
"./OSAL/osal_snv_wrapper.obj" \
"./OSAL/osal_timers.obj" \
"./PROFILES/gap.obj" \
"./PROFILES/gapbondmgr.obj" \
"./PROFILES/gattservapp_util.obj" \
"./PROFILES/sm_ecc.obj" \
"./ROM/common_rom_init.obj" \
"./ROM/rom_init.obj" \
"./Startup/ble_user_config.obj" \
"./Startup/icall_startup.obj" \
"./Startup/osal_icall_ble.obj" \
"./TOOLS/onboard.obj" \

-include ../makefile.init

RM := rm -rf
RMDIR := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include HAL/Common/subdir_vars.mk
-include HAL/Target/CC2650/Drivers/subdir_vars.mk
-include HAL/Target/CC2650/_common/subdir_vars.mk
-include Host/subdir_vars.mk
-include ICallBLE/subdir_vars.mk
-include NPI/subdir_vars.mk
-include OSAL/subdir_vars.mk
-include PROFILES/subdir_vars.mk
-include ROM/subdir_vars.mk
-include Startup/subdir_vars.mk
-include TOOLS/subdir_vars.mk
-include HAL/Common/subdir_rules.mk
-include HAL/Target/CC2650/Drivers/subdir_rules.mk
-include HAL/Target/CC2650/_common/subdir_rules.mk
-include Host/subdir_rules.mk
-include ICallBLE/subdir_rules.mk
-include NPI/subdir_rules.mk
-include OSAL/subdir_rules.mk
-include PROFILES/subdir_rules.mk
-include ROM/subdir_rules.mk
-include Startup/subdir_rules.mk
-include TOOLS/subdir_rules.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C55_DEPS)),)
-include $(C55_DEPS)
endif
ifneq ($(strip $(C_UPPER_DEPS)),)
-include $(C_UPPER_DEPS)
endif
ifneq ($(strip $(S67_DEPS)),)
-include $(S67_DEPS)
endif
ifneq ($(strip $(S62_DEPS)),)
-include $(S62_DEPS)
endif
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(OPT_DEPS)),)
-include $(OPT_DEPS)
endif
ifneq ($(strip $(C??_DEPS)),)
-include $(C??_DEPS)
endif
ifneq ($(strip $(ASM_UPPER_DEPS)),)
-include $(ASM_UPPER_DEPS)
endif
ifneq ($(strip $(S??_DEPS)),)
-include $(S??_DEPS)
endif
ifneq ($(strip $(C64_DEPS)),)
-include $(C64_DEPS)
endif
ifneq ($(strip $(CXX_DEPS)),)
-include $(CXX_DEPS)
endif
ifneq ($(strip $(S64_DEPS)),)
-include $(S64_DEPS)
endif
ifneq ($(strip $(INO_DEPS)),)
-include $(INO_DEPS)
endif
ifneq ($(strip $(CLA_DEPS)),)
-include $(CLA_DEPS)
endif
ifneq ($(strip $(S55_DEPS)),)
-include $(S55_DEPS)
endif
ifneq ($(strip $(SV7A_DEPS)),)
-include $(SV7A_DEPS)
endif
ifneq ($(strip $(C62_DEPS)),)
-include $(C62_DEPS)
endif
ifneq ($(strip $(C67_DEPS)),)
-include $(C67_DEPS)
endif
ifneq ($(strip $(PDE_DEPS)),)
-include $(PDE_DEPS)
endif
ifneq ($(strip $(K_DEPS)),)
-include $(K_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
ifneq ($(strip $(CC_DEPS)),)
-include $(CC_DEPS)
endif
ifneq ($(strip $(C++_DEPS)),)
-include $(C++_DEPS)
endif
ifneq ($(strip $(C43_DEPS)),)
-include $(C43_DEPS)
endif
ifneq ($(strip $(S43_DEPS)),)
-include $(S43_DEPS)
endif
ifneq ($(strip $(ASM_DEPS)),)
-include $(ASM_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(CPP_DEPS)),)
-include $(CPP_DEPS)
endif
ifneq ($(strip $(SA_DEPS)),)
-include $(SA_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
LIB_OUTPUTS += \
simple_peripheral_cc2640r2lp_stack_library.lib \

LIB_OUTPUTS__QUOTED += \
"simple_peripheral_cc2640r2lp_stack_library.lib" \


# All Target
all:
	@$(MAKE) --no-print-directory pre-build
	@$(MAKE) --no-print-directory main-build

# Main-build Target
main-build: simple_peripheral_cc2640r2lp_stack_library.lib

# Tool invocations
simple_peripheral_cc2640r2lp_stack_library.lib: $(OBJS)
ifneq ($(strip $(ORDERED_OBJS)),)
	@echo 'Building target: "$@"'
	@echo 'Invoking: ARM Archiver'
	"/opt/ti/ccs930/ccs/tools/compiler/ti-cgt-arm_18.12.4.LTS/bin/armar" r "simple_peripheral_cc2640r2lp_stack_library.lib" $(ORDERED_OBJS)
	@echo 'Finished building target: "$@"'
	@echo ' '
endif

# Other Targets
clean:
	-$(RM) $(LIB_OUTPUTS__QUOTED)
	-$(RM) "HAL/Common/hal_assert.obj" "HAL/Target/CC2650/Drivers/hal_flash_wrapper.obj" "HAL/Target/CC2650/Drivers/hal_rtc_wrapper.obj" "HAL/Target/CC2650/Drivers/hal_trng_wrapper.obj" "HAL/Target/CC2650/_common/mb_patch.obj" "Host/gatt_uuid.obj" "ICallBLE/ble_dispatch_JT.obj" "ICallBLE/ble_dispatch_lite.obj" "ICallBLE/icall_lite_translation.obj" "NPI/npi.obj" "OSAL/osal.obj" "OSAL/osal_bufmgr.obj" "OSAL/osal_cbtimer.obj" "OSAL/osal_clock.obj" "OSAL/osal_memory_icall.obj" "OSAL/osal_pwrmgr.obj" "OSAL/osal_snv_wrapper.obj" "OSAL/osal_timers.obj" "PROFILES/gap.obj" "PROFILES/gapbondmgr.obj" "PROFILES/gattservapp_util.obj" "PROFILES/sm_ecc.obj" "ROM/common_rom_init.obj" "ROM/rom_init.obj" "Startup/ble_user_config.obj" "Startup/icall_startup.obj" "Startup/osal_icall_ble.obj" "TOOLS/onboard.obj" 
	-$(RM) "HAL/Common/hal_assert.d" "HAL/Target/CC2650/Drivers/hal_flash_wrapper.d" "HAL/Target/CC2650/Drivers/hal_rtc_wrapper.d" "HAL/Target/CC2650/Drivers/hal_trng_wrapper.d" "HAL/Target/CC2650/_common/mb_patch.d" "Host/gatt_uuid.d" "ICallBLE/ble_dispatch_JT.d" "ICallBLE/ble_dispatch_lite.d" "ICallBLE/icall_lite_translation.d" "NPI/npi.d" "OSAL/osal.d" "OSAL/osal_bufmgr.d" "OSAL/osal_cbtimer.d" "OSAL/osal_clock.d" "OSAL/osal_memory_icall.d" "OSAL/osal_pwrmgr.d" "OSAL/osal_snv_wrapper.d" "OSAL/osal_timers.d" "PROFILES/gap.d" "PROFILES/gapbondmgr.d" "PROFILES/gattservapp_util.d" "PROFILES/sm_ecc.d" "ROM/common_rom_init.d" "ROM/rom_init.d" "Startup/ble_user_config.d" "Startup/icall_startup.d" "Startup/osal_icall_ble.d" "TOOLS/onboard.d" 
	-@echo 'Finished clean'
	-@echo ' '

pre-build:
	-/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/../../../tools/blestack/lib_search/lib_search         /home/aaron/Documentos/Trabajo/interaction-tracker-master/simple_peripheral_cc2640r2lp_stack_library/TOOLS/build_config.opt         /home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/blelib         /home/aaron/Documentos/Trabajo/ccs-workspace/simple_peripheral_cc2640r2lp_stack_library/FlashROM_Library/lib_linker.cmd         cc2640         /home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/../../../tools/blestack/lib_search/lib_search.xml         /home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack/symbols
	-@echo ' '

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets

