# kuigeskills

奎哥的 Agent Skills 合集 | Kuige's collection of agent skills for [ZCode](https://zcode.ai).

## Skills

| Skill | 说明 |
| --- | --- |
| [ip-logo-generator](./ip-logo-generator/) | 生成高度简化、圆润、微新拟物风格的 IP 吉祥物/品牌角色图提示词。适用于头像、吉祥物、空状态插图，可直接投喂 GPT Image / Seedance 等生图模型。 |

## 安装

把对应 skill 目录复制到用户级 skills 目录即可被 ZCode 发现：

```bash
git clone https://github.com/Tliens/kuigeskills.git
mkdir -p ~/.agents/skills
cp -r kuigeskills/ip-logo-generator ~/.agents/skills/
```

## License

MIT
