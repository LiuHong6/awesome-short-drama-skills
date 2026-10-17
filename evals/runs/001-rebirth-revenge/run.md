# 第一轮：剧本类 skill · 《双面绣》

- 梗概：[premises/001-rebirth-revenge.md](../../premises/001-rebirth-revenge.md)（重生复仇，红果竖屏，60 集，每集 1–2 分钟）
- 交付要求：人物小传、60 集分集大纲（标出付费卡点）、第 1–3 集完整剧本
- 运行时间：2026-10-17（北京时间）
- 环境：Claude Code 2.1.302，模型 claude-opus-5-5，推理强度 high，每个 skill 跑 1 次
- 运行器：[evals/run.py](../../run.py)，任何人都可以用同样的命令复现

## 统一指令

每个 skill 用同一条开场指令和同一条固定回复，不额外加指令：

- 开场（有入口 skill 的）：`/<入口 skill> 请完成 premise.md 里的短剧创作需求，交付物写成文件放在当前目录。`
- 开场（工具箱型仓库）：`请使用已安装的 skill，完成 premise.md 里的短剧创作需求，交付物写成文件放在当前目录。`
- 对照组：`请完成 premise.md 里的短剧创作需求，交付物写成文件放在当前目录。`
- agent 停下来提问或等确认时，统一回复：`需求都在 premise.md 里，里面没写的你来定，不用再问我。请继续，直到 premise.md 列出的三项交付都写成文件。`

skill 按 skills CLI 的默认范围安装：仓库里所有 SKILL.md 所在目录复制进工作目录的 `.claude/skills/`。

## 参赛名单

| 项目 | 测试版本 | 入口 | 装了几个 skill | 轮数 | 耗时 | 按 API 价格折算 | 文件 |
|---|---|---|---|---|---|---|---|
| 对照组（不装 skill） | — | — | 0 | 1 | 13 分钟 | $2.01 | [产出](baseline/output/) · [记录](baseline/transcript.md) |
| [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) | [`d28a9c5`](https://github.com/eternityspring/shuohao-skills/tree/d28a9c539b40523d081794b25ff9113016bd98e0) | `/novel-outline` | 7 | 4 | 16 分钟 | $14.54 | [产出](eternityspring__shuohao-skills/output/) · [记录](eternityspring__shuohao-skills/transcript.md) |
| [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | [`dafe80e`](https://github.com/zenstory-ai/drama-skills/tree/dafe80ee390ec8be5a7ec8dd156a84d511f8e7dd) | `/short-drama` | 12 | 2 | 13 分钟 | $5.19 | [产出](zenstory-ai__drama-skills/output/) · [记录](zenstory-ai__drama-skills/transcript.md) |
| [lixiaoxiao9888-create/manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) | [`370a236`](https://github.com/lixiaoxiao9888-create/manju-laoli-skill/tree/370a236ed47d29ef3bf356ced85a17cee2f117a4) | `/short-drama-director` | 13 | 3 | 18 分钟 | $13.24 | [产出](lixiaoxiao9888-create__manju-laoli-skill/output/) · [记录](lixiaoxiao9888-create__manju-laoli-skill/transcript.md) |
| [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | [`51115f1`](https://github.com/jtydhr88/screenwriting-skills/tree/51115f18d160aa8b2ac5813e4432b6f0b425358f) | 不指定 | 26 | 1 | 12 分钟 | $2.47 | [产出](jtydhr88__screenwriting-skills/output/) · [记录](jtydhr88__screenwriting-skills/transcript.md) |
| [Shanyin-ai/shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) | [`ca20ce2`](https://github.com/Shanyin-ai/shanyin-screenwriting-master/tree/ca20ce245ae028e64418393d6cf4688b7dbe3d89) | `/screenwriting-master` | 1 | 1 | 14 分钟 | $2.58 | [产出](Shanyin-ai__shanyin-screenwriting-master/output/) · [记录](Shanyin-ai__shanyin-screenwriting-master/transcript.md) |
| [lixiaoxiao9888-create/short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) | [`1a634aa`](https://github.com/lixiaoxiao9888-create/short-drama-factory/tree/1a634aa852cb976be1e6a915845480f6b1126693) | `/short-drama-factory` | 1 | 1 | 19 分钟 | $4.13 | [产出](lixiaoxiao9888-create__short-drama-factory/output/) · [记录](lixiaoxiao9888-create__short-drama-factory/transcript.md) |
| [adoria111/emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills) | [`919292c`](https://github.com/adoria111/emma-screenwriting-skills/tree/919292cabf7b5b3ebd1027c72f1d0b711a16c189) | `/em-story-architect` | 10 | 3 | 20 分钟 | $10.38 | [产出](adoria111__emma-screenwriting-skills/output/) · [记录](adoria111__emma-screenwriting-skills/transcript.md) |
| [zhu5859243-free/hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting) | [`d9c235a`](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting/tree/d9c235a6bc0be67d7563018cf3db49bcf58e72ab) | `/hongguo-shortdrama-screenwriting` | 1 | 1 | 16 分钟 | $3.28 | [产出](zhu5859243-free__hongguo-shortdrama-screenwriting/output/) · [记录](zhu5859243-free__hongguo-shortdrama-screenwriting/transcript.md) |
| [catyiqian/qianqianwriting](https://github.com/catyiqian/qianqianwriting) | [`436088b`](https://github.com/catyiqian/qianqianwriting/tree/436088b3bb2ebeae5cf26663fa92525512460f5b) | `/qianqianwriting` | 1 | 2 | 13 分钟 | $4.39 | [产出](catyiqian__qianqianwriting/output/) · [记录](catyiqian__qianqianwriting/transcript.md) |
| [Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama) | [`a1a00d3`](https://github.com/Hao0321/ai-short-drama/tree/a1a00d3949fedd74edb6830a79d189a2c76920db) | `/ai-short-drama` | 1 | 2 | 24 分钟 | $8.33 | [产出](Hao0321__ai-short-drama/output/) · [记录](Hao0321__ai-short-drama/transcript.md) |

## 这一轮的限制

- **不运行脚本。** 为了安全，agent 只能读写自己的工作目录，不能运行命令、不能联网、不连 MCP。shuohao-skills、zenstory drama-skills、漫剧老李、short-drama-factory、hongguo、ai-short-drama 都带校验脚本，这一轮里这些脚本没有跑，agent 改用手工核对，记录里写明了。产出的文字由模型照着 skill 的方法写成，脚本主要做格式和时长校验，但完整流程确实没有走全。
- **只跑一次。** 同一个 skill 换一次运行，产出会不同。这一轮每个只跑一次，产出全部原样保留。
- **开场指令要求直接交文件。** 有的 skill 原本会在大纲之后停下来等用户确认，再进入剧本环节（例如 shuohao-skills 的 novel-outline → novel-script）。统一回复让 agent 自己做决定，所以这类确认环节被跳过了。
- **两个参赛项目同源。** hongguo-shortdrama-screenwriting 基于 short-drama-factory v3.2 改编，README 已注明。
- **两个参赛项目不专做短剧。** jtydhr88/screenwriting-skills 的 README 写明不计划覆盖竖屏短剧；山音编剧大师的剧集模板按 8–24 集、每集 10–60 分钟设计。它们参赛是为了看通用编剧方法放到短剧上的表现。

## 怎么评

产出先去掉文件名和文中能认出 skill 的字样，随机编成 A–K，交给两位评审盲评：一位看第 1–3 集剧本，一位看人物小传和分集大纲。评审由 AI（Claude Opus 5.5）完成，编辑核对了引文和结论后再揭晓对应关系。点评见 [review.md](review.md)。
