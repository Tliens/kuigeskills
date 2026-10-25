# kuigeskills

奎哥的 Agent Skills 合集 | Kuige's collection of agent skills for [ZCode](https://zcode.ai).

## Skills

| Skill | 说明 |
| --- | --- |
| [ip-logo-generator](./ip-logo-generator/) | 生成高度简化、圆润、微新拟物风格的 IP 吉祥物/品牌角色图提示词。适用于头像、吉祥物、空状态插图，可直接投喂 GPT Image / Seedance 等生图模型。 |
| [appstore-product](./appstore-product/) | 制作、重做和审查可提交的 App Store 普通截图、自定产品页截图，以及“标题和搜索结果”创意素材；包含内容策划、商用素材追溯、安全区和图片规格自动验收。 |

## 安装

把对应 skill 目录复制到用户级 skills 目录即可被 ZCode 发现：

```bash
git clone https://github.com/Tliens/kuigeskills.git
mkdir -p ~/.agents/skills
cp -r kuigeskills/<skill-name> ~/.agents/skills/
```

Codex 用户也可以安装到 `~/.codex/skills`：

```bash
mkdir -p ~/.codex/skills
cp -r kuigeskills/<skill-name> ~/.codex/skills/
```

## License

MIT
