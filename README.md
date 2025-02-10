# AI写作助手

## 项目简介
AI写作助手是一个基于Python开发的智能写作工具，旨在帮助作者更高效地进行创作。本工具主要基于Deepseek R3 API，提供直观的界面操作，让创作过程更加流畅自然。

## 核心功能
### 1. 智能配置系统
- Deepseek R3 API集成
- API密钥管理
- 完全自定义提示词系统
- 提示词历史记录

### 2. 项目管理
- 多项目并行管理
- 项目分类与搜索
- 项目进度追踪
- 自动保存与备份

### 3. 章节管理
- 灵活的章节组织
- 智能续写
- 上下文关联
- 内容版本控制

### 4. AI辅助创作
- 自定义提示词编辑器
- 上下文智能关联
- 实时AI反馈
- 多轮对话优化

### 5. 导出功能
- Word文档导出（.docx）
- PDF文档导出
- 纯文本导出（.txt）

## 技术架构
### 前端界面
- 使用PyQt6构建现代化GUI界面
- 响应式三栏布局设计
- 深色/浅色主题支持
  ```
  浅色主题：
  - 背景：#FFFFFF
  - 文本：#333333
  - 强调：#007AFF

  深色主题：
  - 背景：#1E1E1E
  - 文本：#FFFFFF
  - 强调：#0A84FF
  ```

### 后端架构
- SQLite数据库存储
- 模块化设计架构
- 异步AI调用处理
- 本地数据加密存储

### 数据库设计
```sql
-- 项目表
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 章节表
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    title TEXT NOT NULL,
    content TEXT,
    prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- 设置表
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    api_key TEXT,
    theme_mode TEXT DEFAULT 'light',
    last_project_id INTEGER,
    FOREIGN KEY (last_project_id) REFERENCES projects(id)
);
```

### 开发规范
- Python 3.8+
- PEP 8编码规范
- 类型提示支持
- 完整单元测试
- 详细代码注释

## 项目结构
```
ai_writing_assistant/
├── src/
│   ├── gui/                 # GUI相关模块
│   │   ├── main_window.py   # 主窗口
│   │   ├── project_list.py  # 项目列表组件
│   │   ├── chapter_list.py  # 章节列表组件
│   │   ├── editor.py        # 编辑器组件
│   │   └── themes/          # 主题样式
│   ├── core/                # 核心功能模块
│   │   ├── project.py       # 项目管理
│   │   ├── chapter.py       # 章节管理
│   │   └── settings.py      # 设置管理
│   ├── database/            # 数据库操作模块
│   │   ├── models.py        # 数据模型
│   │   └── operations.py    # 数据库操作
│   ├── ai_services/         # AI服务模块
│   │   ├── deepseek.py      # Deepseek API封装
│   │   └── prompt.py        # 提示词处理
│   └── utils/               # 工具函数模块
│       ├── exporter.py      # 导出功能
│       └── logger.py        # 日志功能
├── tests/                   # 测试用例
├── docs/                    # 项目文档
├── resources/               # 资源文件
└── config/                  # 配置文件
```

## 开发计划
### 第一阶段：基础架构搭建
- [x] 项目初始化
- [ ] 数据库设计与实现
- [ ] GUI框架搭建（含深色模式）
- [ ] Deepseek R3 API接入

### 第二阶段：核心功能开发
- [ ] 项目管理系统
- [ ] 章节管理系统
- [ ] 提示词编辑器
- [ ] AI交互功能

### 第三阶段：扩展功能
- [ ] 文档导出功能
- [ ] 主题切换系统
- [ ] 自动保存功能
- [ ] 性能优化

## 环境要求
- Python 3.8+
- PyQt6
- SQLite3
- python-docx（Word导出）
- reportlab（PDF导出）
- Deepseek API密钥

## 使用说明
（待开发完成后补充）

## 注意事项
- 请妥善保管API密钥
- 定期备份项目数据
- 遵循Deepseek API使用规范
- 建议定期保存文档 