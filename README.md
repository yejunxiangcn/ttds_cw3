## 项目结构

```
TTDS_CW3
├─ static
│    ├─ englishST.txt				  停用词
│    └─ search_mock.json			mock数据
├─ api.py							           业务类
├─ app.py							           启动、配置文件
├─ controller.py				      	请求处理和页面跳转
├─ service.py						        业务实现，对业务类进行调用
├─ result.py						         结果类，前后端分离时作为交互数据的格式规范（预弃用）
└─ utils.py							         工具封装
```

 

## 待完成

- 前端

  - 搜索框
    - 主体
    - Bool
    - 显示补全
    - 是否搜索description
  - 搜索结果界面
  - 具体页面

  

- 补全

  - 最多10个title

  

- stop words
- tfidf



- 数据存放（倒排索引+记录）
  - 文件系统+cache
  - 直接使用字典 {word: id: [pos1, pos2]} 
    - 初始化字典大小

- bool搜索



- 测试

- 部署
