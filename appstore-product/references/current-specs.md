# 当前规格基线

以下内容于 **2026-10-25** 对照 Apple 官方文档核验。每次任务仍须重新打开官方页面；若页面与本文件冲突，以实时官方页面为准，并更新制作参数，不要盲从脚本基线。

## 官方入口

- Screenshot Specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Creative Assets Specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications/
- Asset Best Practices: https://developer.apple.com/app-store/asset-best-practices/
- Manage Your App Store Assets: https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets
- Creating Your Product Page: https://developer.apple.com/app-store/product-page/
- Custom Product Pages: https://developer.apple.com/help/app-store-connect/create-custom-product-pages/configure-multiple-product-page-versions/

## 普通截图当前必需显示尺寸

- iPhone：至少一张 Dynamic Island 中型显示屏截图；可接受竖图 `1179×2556` 或 `1206×2622`，横图为对应转置。
- iPad：如果 App 支持 iPadOS，至少一张 13 英寸显示屏截图；可接受竖图 `2064×2752` 或 `2048×2732`，横图为对应转置。
- 每个设备尺寸 1–10 张，JPEG/JPG/PNG，无 alpha 或透明度。
- 如果 UI 在多设备尺寸间一致，可仅提供最高必需分辨率，由 App Store Connect 缩放；如果布局差异明显，应按设备重新制作。

只把这些尺寸当作“当前最小提交路径”，不要据此否定用户明确要求的其他兼容尺寸。官方页面已列出更多机型与尺寸，也可能新增设备要求。

## 标题和搜索结果静态创意素材

| 版位 | 比例 | 分辨率 | 格式 |
|---|---:|---:|---|
| Product Page Header | 21:9 | `3840×1646` | JPEG/JPG/PNG |
| Search Results | 3:2 | 最小 `1920×1280`，最大 `3840×2560` | JPEG/JPG/PNG |
| Universal | 16:9 | `5244×2950` | PNG |

均不得包含 alpha 或透明度。

## 官方模板中提取的安全区基线

坐标原点在左上角，单位为像素：

| 画布 | 安全区 x | y | 宽 | 高 |
|---|---:|---:|---:|---:|
| Header `3840×1646` | 1097 | 493 | 1646 | 661 |
| Search `3840×2560` | 836 | 765 | 2168 | 1030 |
| Universal `5244×2950` | 1921 | 660 | 1402 | 962 |

安全区用于保护主文案、品牌标识和不可裁切的焦点，不要求所有背景和装饰都缩进安全区。允许有意出血，但被裁后仍应保持完整语义。制作前优先重新下载 Apple 当前模板，并在 App Store Connect Preview 中检查。

## 当前内容政策要点

- 普通截图和预览展示 App 使用中的真实体验。
- Creative Assets 可以表达品牌、季节内容和新内容，但必须与 App 功能相关。
- 不放具体价格、折扣、网址、版权符号、其他平台或商店标志、未经证实的奖项或 Apple 荣誉标识。
- 所有面向 App Store 展示的创意素材应适合 4+ 年龄层。
- 创意素材目前面向运行 iOS 27 或 iPadOS 27 及以上的 App 和游戏；提交前仍需核对当时的资格说明。
