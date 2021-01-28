import wmi
obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)

# displays = [x for x in obj if 'DISPLAY' in str(x)]
displays = [x for x in obj if x.PNPClass == 'Monitor']

for item in displays:
    print(item)
    # if item.Name == 'Dell S2240T(HDMI)':
    #     print('Yep')
