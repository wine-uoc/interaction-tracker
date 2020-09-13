#
_XDCBUILDCOUNT = 
ifneq (,$(findstring path,$(_USEXDCENV_)))
override XDCPATH = /home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source;/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/kernel/tirtos/packages;/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack
override XDCROOT = /opt/ti/ccs930/xdctools_3_60_02_34_core
override XDCBUILDCFG = ./config.bld
endif
ifneq (,$(findstring args,$(_USEXDCENV_)))
override XDCARGS = 
override XDCTARGETS = 
endif
#
ifeq (0,1)
PKGPATH = /home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source;/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/kernel/tirtos/packages;/home/aaron/ti/simplelink_cc2640r2_sdk_4_20_00_04/source/ti/blestack;/opt/ti/ccs930/xdctools_3_60_02_34_core/packages;..
HOSTOS = Linux
endif
