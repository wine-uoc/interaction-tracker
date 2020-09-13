#
_XDCBUILDCOUNT = 
ifneq (,$(findstring path,$(_USEXDCENV_)))
override XDCPATH = /home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source;/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/kernel/tirtos/packages;/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack
override XDCROOT = /opt/ti/ccs930/xdctools_3_60_02_34_core
override XDCBUILDCFG = ./config.bld
endif
ifneq (,$(findstring args,$(_USEXDCENV_)))
override XDCARGS = 
override XDCTARGETS = 
endif
#
ifeq (0,1)
PKGPATH = /home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source;/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/kernel/tirtos/packages;/home/aaron/Documentos/Trabajo/CCS9.3.0.00012_linux-x64/ti/simplelink_cc2640r2_sdk_3_40_00_10/source/ti/blestack;/opt/ti/ccs930/xdctools_3_60_02_34_core/packages;..
HOSTOS = Linux
endif
