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

打包好并写好签名的版本：
通过网盘分享的文件：浩讯亿通cpu测试工具.zip
链接: https://pan.baidu.com/s/1Odm9VxiOXNjEX0--jScgLA?pwd=hxyt 提取码: hxyt 复制这段内容后打开百度网盘手机App，操作更方便哦
下载就可以直接使用！！！

程序截图：
<img width="803" height="763" alt="屏幕截图 2025-07-12 172919" src="https://github.com/user-attachments/assets/3b675042-3f7e-4f92-a708-88ea88baf6d4" />
<img width="800" height="761" alt="屏幕截图 2025-07-12 172805" src="https://github.com/user-attachments/assets/05d4c25d-f329-4628-b62e-43a0ae85e902" />
<img width="803" height="762" alt="屏幕截图 2025-07-12 172819" src="https://github.com/user-attachments/assets/4345b8d3-d78d-4b86-afe3-fe3f2e202814" />
<img width="805" height="763" alt="屏幕截图 2025-07-12 172830" src="https://github.com/user-attachments/assets/22e87d71-db2b-4902-9769-4a41d56c0047" />
<img width="802" height="765" alt="屏幕截图 2025-07-12 172839" src="https://github.com/user-attachments/assets/cd808827-3807-49c5-a34e-43b29b1d4756" />
<img width="802" height="763" alt="屏幕截图 2025-07-12 172849" src="https://github.com/user-attachments/assets/7e22dbc3-84f9-4b36-851b-2380b9a1d06c" />
<img width="801" height="763" alt="屏幕截图 2025-07-12 172857" src="https://github.com/user-attachments/assets/dd9c67ff-4bd6-4eb5-9dda-689a854d82ed" />
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
8.新增电脑配置查询功能
