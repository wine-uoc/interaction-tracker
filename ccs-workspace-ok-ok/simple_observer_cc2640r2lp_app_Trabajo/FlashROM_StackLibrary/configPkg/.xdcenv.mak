#
_XDCBUILDCOUNT = 
ifneq (,$(findstring path,$(_USEXDCENV_)))
override XDCPATH = /home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source;/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/kernel/tirtos/packages;/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack
override XDCROOT = /home/aaron/ti/xdctools_3_51_03_28_core
override XDCBUILDCFG = ./config.bld
endif
ifneq (,$(findstring args,$(_USEXDCENV_)))
override XDCARGS = 
override XDCTARGETS = 
endif
#
ifeq (0,1)
PKGPATH = /home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source;/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/kernel/tirtos/packages;/home/aaron/ti/simplelink_cc2640r2_sdk_4_30_00_08/source/ti/blestack;/home/aaron/ti/xdctools_3_51_03_28_core/packages;..
HOSTOS = Linux
endif
