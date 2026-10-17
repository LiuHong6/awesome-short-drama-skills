# 第一轮点评：剧本类 skill · 《双面绣》

同一个梗概，交给 10 个剧本类 skill 和 1 个不装 skill 的对照组。每组都在同一个 agent、同一个模型下各跑一次，环境和限制见 [run.md](run.md)。

产出先匿名成 A–K，由两位评审盲评：
- [剧本评审](review-scripts.md)：第 1–3 集，看钩子、对白、AI 味、可用性和贴合需求。
- [大纲评审](review-outlines.md)：人物小传和 60 集分集大纲，看人物、结构、重生设定和可用性。

这一页是两份评审的摘要。不打总分，每条结论都能在评审原文和产出里找到出处。

## 先说结论

**1. 故事骨架高度趋同，装不装 skill 都一样。** 11 份产出不约而同地做了同样的选择：
- 都有一个叫「小满」的角色。
- 首个付费卡点都在第 10 集。
- 都发明了藏在针脚里、靠侧光或透光显形的名字，当作核心证据。
- 都把抄袭的源头推到上一代。
- 都让前世那场火在今生重演。
- 10 份从前世火场开场；5 份的退婚台词一字不差，都是「这婚，我不订了。」
- 有 3 份的顾家母亲都叫周曼琳。

skill 改变的主要是写法、格式和节奏纪律，很少改变故事本身。放到同一个平台上，这些开头的前 30 秒很难分清。用 skill 写短剧，独特的设定仍然要靠人给。

**2. 对照组的问题集中在时长和「开挂」。** 不装 skill 的那份苏绣画面并不少，但有三个问题：
- 每集篇幅约是 2 分钟上限的 1.5–2 倍。
- VO 长、比喻多，还有拍不出来的心理说明。
- 女主的先知几乎从不失手。

装了 skill 的稿子大多在时长、格式和「先知要付代价」上更像短剧。不过这一轮每组只跑了一次，这只能算观察，还不是定论。

**3. 通用编剧 skill 并不吃亏。**
- screenwriting-skills 的 README 写明不做竖屏短剧，山音编剧大师的模板按 10–60 分钟一集设计。这一轮里，它们在人物、对白和 AI 味上都排在前面。
- 专做短剧的 skill 强在另一些地方：
  - 卡点更准：hongguo、short-drama-factory 的第 10 集。
  - 制作更省：short-drama-factory 前三集只有 4 个场景，没有火戏。
  - 资产清单更完整：shuohao。

**4. 交给剧组之前都要清理。**
- 多份剧本带着系统字段：逐集元数据头、debt/entity ID、emoji 检查点、【钩子】行。
- 没有一份给出逐集的场景、人物、道具表。

## 逐个看

| 盲评 | 项目 | 写得好的地方 | 主要问题 |
|---|---|---|---|
| A | [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 开场 10 秒交代了火、罪名和神秘救援者。第 3 集结尾「你带走的，只是纸。」是全场最好的钩子之一。对白省，AI 味轻，三集都在 1–2 分钟。卡点附依赖事实表，先知列出了失准的集数 | 前三集几乎没有针线技艺的画面；关键危机靠陆川解围 |
| B | [Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama) | 苏绣观赏性全场最强（烧线辨丝、侧光显字），每集都有观众能亲眼验证的技艺打脸。视觉锚和声音卡适合 AI 生成 | 第 1 集可能超过 2 分钟，制作量全场最重之一；剧本里夹着 debt/entity ID 等系统字段；终局对手从顾家移到了新人物 |
| C | [lixiaoxiao9888-create/manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) | 有劈丝的技艺画面。顾晚是从没被允许署名的设计师，成了女主的镜像。先知只知公开信息，第 10 集用先知抢单反被咬 | 第 1 集有超时风险，第 2 集结尾偏静；前 20 集女主输多赢少；第 55–56 集高潮过薄 |
| D | [catyiqian/qianqianwriting](https://github.com/catyiqian/qianqianwriting) | 大纲最守「每集 2–3 句」；藏名显字、劈丝有画面 | 三集有 19 句 OS，AI 味偏重；直播自证用了六次；第 26 集庭审胜诉直接靠前世记忆；第 54 集的显字反转有漏洞 |
| E | [zhu5859243-free/hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting) | 第 10 集卡点（粉包落下前半秒）和拍粉验稿的反转最扎实；前三集只用 3 个场景 | 剧本自标 115 秒，实际约 1 分钟；台词句句是金句，人物声音混在一起；约 36 集大纲超过 3 句；和 short-drama-factory 用同一套框架 |
| F | [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | 打火机的「咔嗒」声把前世凶手和今生的一通电话连起来。人物全场最好之一：顾晚是当年偷稿者的女儿。AI 味轻，自带超时删减规则；先知有代价（第 31 集凭记忆冤枉了人） | 第 20 集卡点偏弱；这是通用编剧 skill，README 写明不做竖屏短剧 |
| G | [Shanyin-ai/shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) | 对白全场最好之一（外婆一句「锅里有粥。」），全程没有 OS。顾晚有真师承。第 58 集显字的是母亲原作，反转不用另作解释 | 第 1 集有超时风险，制作量重；第 40–46 集连续七集下坠；文档里的 emoji 检查点要清掉 |
| H | [lixiaoxiao9888-create/short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) | 唯一不从火场开场的一份，直接从订婚宴签字切入。制作量最轻（4 个场景，没有火）。第 10 集卡点（拉电闸）精准，单列了备案类别 | 对白几乎只用「借对方的话反问」一种句式；前两集结尾重复；前三集几乎没有苏绣画面；反派接近单纯的恶；第 57 集反转有漏洞 |
| I | 对照组（不装 skill） | 苏绣画面多（回针藏名、劈丝） | 每集篇幅是上限的 1.5–2 倍；VO 长，比喻多；先知几乎从不失手；反派动机单一 |
| J | [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) | 资产清单最完整（17 个人物编号、13 个场景、7 件道具），最贴近制片；时长合规 | 唯一第 1 集没有退婚（推到第 2 集）；大纲每集约 55 字，最薄；反派五次都靠物理破坏。注意：这一轮没跑它的校验脚本，剧本也没走 novel-script 流程（见 [run.md](run.md)） |
| K | [adoria111/emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills) | 格式最接近行业标准，时长合规。人物全场最好之一：陆川经由母亲接进主线，却从不替女主赢。翡翠镯线索埋得最好。先知的代价最重（留着内鬼，结果外婆被烧伤）。知情节奏表适合编剧室 | 前三集苏绣画面少；退婚现场靠私情做证据；第 20 集卡点偏弱；第 54–58 集揭示扎堆 |

## 这一轮能说明什么，不能说明什么

- **能说明的**：在同一个模型下，这些 skill 会把产出往哪个方向推，比如时长、格式、人物代价和卡点纪律。
- **不能说明的**：
  - 换一个模型、多跑几次，结果会不会变。
  - 让 skill 跑脚本、走完确认环节之后会不会更好。
- **下一轮的计划**：在隔离环境里允许运行脚本，每个 skill 多跑几次，并请人类编剧参与评审。
