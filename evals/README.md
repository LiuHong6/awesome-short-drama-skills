# 实测对比

列表里的「人工核对」只说明项目信息准确。这里放实测：同一个题材交给不同的 skill，把产出并排摆出来，让读者自己判断。

## 实测规范

每轮实测：

1. **同一份输入**：一个梗概（premise），放在 `premises/` 下，所有参赛 skill 共用。
2. **同一个环境**：同一个 agent、同一个模型、同样的推理强度，记录版本号。
3. **固定 skill 版本**：记录每个仓库的 commit hash。
4. **按 skill 自己的流程走**：skill 要问答就如实回答，不额外加指令；回答内容统一记录在 `run.md` 里。
5. **完整保留产出**：不挑最好的一次，跑几次就放几次。

## 目录结构

```
evals/
├── run.py                     # 运行器：在隔离目录里用 Claude Code 无头模式跑一个 skill
├── premises/
│   └── 001-<题材>.md          # 梗概：题材、体裁、篇幅要求
└── runs/
    └── 001-<题材>/
        ├── contestants.toml   # 参赛名单和入口 skill
        ├── run.md             # 环境、版本、统一指令、参赛 skill 的 commit、限制
        ├── <owner>__<repo>/   # 每个 skill 的产出（output/）、问答记录（transcript.md）、运行信息（run.json）
        ├── review.md          # 点评摘要
        └── review-*.md        # 盲评原文
```

## 已完成的轮次

- [第一轮：剧本类 skill · 《双面绣》](runs/001-rebirth-revenge/review.md)（2026-10-17）：10 个剧本 skill 加 1 个不装 skill 的对照组

## 复现

```bash
python evals/run.py 001-rebirth-revenge zenstory-ai/drama-skills --work /tmp/evals
```

需要已登录的 `claude` CLI 和 git。agent 只能读写自己的工作目录，不能运行命令、不能联网、不连 MCP。

## 点评维度

| 维度 | 看什么 |
|---|---|
| 钩子 | 开头 / 每集结尾能不能让人想往下看 |
| 人物 | 动机是否清楚，行为是否前后一致 |
| 结构 | 节奏、冲突升级、反转是否成立 |
| 对白 | 像不像人说的话，有没有角色区分度 |
| AI 味 | 套话、排比、空洞形容词的多少 |
| 可用性 | 产出离能直接用还差多少修改；流程是否顺手 |

点评只写观察和例子，不打总分。
