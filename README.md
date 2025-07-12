╔╗╔╗╔══╗╔══╗╔══╗╔══╗╔╗╔╗╔╗─╔╗╔════╗╔══╗╔╗─╔╗╔═══╗╔══╗╔══╗╔══╗╔╗─╔╗
║║║║║╔╗║║╔╗║╚═╗║║╔═╝║║║║║╚═╝║╚═╗╔═╝║╔╗║║╚═╝║║╔══╝╚═╗║║╔═╝╚╗╔╝║╚═╝║
║╚╝║║╚╝║║║║║──║╚╝║──║║║║║╔╗─║──║║──║║║║║╔╗─║║║╔═╗──║╚╝║───║║─║╔╗─║
║╔╗║║╔╗║║║║║──║╔╗║──║║║║║║╚╗║──║║──║║║║║║╚╗║║║╚╗║──║╔╗║───║║─║║╚╗║
║║║║║║║║║╚╝║╔═╝║║╚═╗║╚╝║║║─║║──║║──║╚╝║║║─║║║╚═╝║╔═╝║║╚═╗╔╝╚╗║║─║║
╚╝╚╝╚╝╚╝╚══╝╚══╝╚══╝╚══╝╚╝─╚╝──╚╝──╚══╝╚╝─╚╝╚═══╝╚══╝╚══╝╚══╝╚╝─╚╝

浩讯亿通cpu专业测试工具1.0.1
开源-免费-绿色-无毒-专业
问题反馈：邮箱zhangyuhao@haoxun.cc（请备注来意，以及遇到的问题并请附带提供截图或视频，感谢支持！）
官方QQ群：182352621
github开源地址：https://github.com/haoxunwl/-cpu-/tree/main
本程序采用python开发，采用MIT开源协议，可二次开发，欢迎大家在基于本程序上开发各种有意思好用好玩的功能！

程序截图：
<img width="806" height="765" alt="屏幕截图 2025-07-12 123929" src="https://github.com/user-attachments/assets/78b99fcd-2f65-4b69-9d3a-ad6d8cc9017b" />
<img width="803" height="766" alt="屏幕截图 2025-07-12 123727" src="https://github.com/user-attachments/assets/49c347f1-6924-4919-9a1b-b5c2da0a0e7b" />
<img width="806" height="771" alt="屏幕截图 2025-07-12 123737" src="https://github.com/user-attachments/assets/2a8b2eb2-1566-445b-9b19-2a21f377cec7" />
<img width="806" height="768" alt="屏幕截图 2025-07-12 123745" src="https://github.com/user-attachments/assets/a21764a8-b8f3-4e75-a57f-14ca369b9e58" />
<img width="805" height="768" alt="屏幕截图 2025-07-12 123755" src="https://github.com/user-attachments/assets/cf58b1d0-b697-4492-95f9-9d64bce9d779" />
<img width="806" height="768" alt="屏幕截图 2025-07-12 123803" src="https://github.com/user-attachments/assets/7ffbfa7a-5540-4445-bb15-cd7d4e56d361" />
<img width="1706" height="1280" alt="浩讯电脑品牌logo" src="https://github.com/user-attachments/assets/3c69445b-d5c6-4d89-80cf-4f9446fcebf6" />


项目开发日志：
2025年6月14日
初代程序版本1.0
1.发布了初代产品程序1.0

2025年7月11日
改进程序版本1.01
1.修复了win11和win10，xp，Linux等系统无法获取的问题
2.修复了个别系统主机闪退打不开问题
3.修复了没有安全证书报毒的问题（本软件现已开源不存在任何病毒，开源地址：https://github.com/haoxunwl/-cpu-/tree/main）
4.将百分制改为千分制
5.修复了cpu电压和频率不准确问题
6.增强电压获取算法，支持多种数据源（OpenHardwareMonitor、WMI、ACPI、sysfs）
7.增加实时显示CPU电压和频率变化曲线
8.主窗口尺寸从1000x900缩小到800x700，所有字体缩小1-2号（Arial 8-10号代替11-12号）内边距/间距优化
9.新增cpu性能监控功能，支持多核心独立频率监控
10.优化了CPU电压模拟算法
11.修复程序在移动和切换页面会卡顿，添加内容变化检测，只在内容实际变化时更新UI，所有UI更新操作使用 root.after() 调度到主线程执行，优化了预热测试的UI更新频率，减少不必要的字符串操作和对象创建


2025年7月12日
改进程序版本1.01
1.新增cpu占用监控功能
2.增加了错误处理和异常捕获
3.减少内存带宽测试的内存大小
4.所有UI相关错误处理都通过队列进行
5.大幅减少所有测试的迭代次数（50-70%）
6.创建了全局的UI更新队列 ui_update_queue
7.移除不必要的UI更新点
