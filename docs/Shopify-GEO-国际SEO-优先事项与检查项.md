# Shopify 跨境电商 · GEO + 国际 SEO 优先事项与检查项

适用于：Shopify 独立站、多市场/多语言、兼顾传统搜索与生成式引擎（GEO）的优化。

---

## 一、优先事项总览

| 优先级 | 事项 | 对应 Shopify 位置 | 预计耗时 |
|--------|------|-------------------|----------|
| **P0** | 市场与语言结构 + hreflang/canonical | 后台 Markets、域名 | 1–2 天 |
| **P0** | 多语言 Sitemap 与 GSC 提交 | 后台、Google Search Console | 0.5 天 |
| **P0** | 产品页结构化数据（Product JSON-LD） | 主题 Liquid 或 App | 1–2 天 |
| **P1** | 标题/描述/URL 与本地化内容 | 后台产品/页面、Translate & Adapt | 持续 |
| **P1** | 每页自引用 canonical 与 hreflang 互链验证 | 主题/App、GSC | 0.5 天 |
| **P1** | Core Web Vitals 与移动端 | 主题、CDN、图片 | 持续 |
| **P2** | FAQ/Article 等 Schema（GEO） | 主题 Liquid 或 App | 1 天 |
| **P2** | llms.txt / AI 抓取策略（可选） | 主题或 App | 0.5 天 |
| **P2** | 本地外链与引用监测 | 站外运营、手动/工具 | 持续 |

---

## 二、P0：必须先做（影响收录与地域正确性）

### 1. 市场与语言结构（Markets + 语言）

**后台路径**：`设置 → 市场（Markets）` / `Settings → Markets`

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 已创建所有目标市场 | 每个国家/地区单独市场或按区域分组 | 后台 Markets 列表与 URL 一致 |
| ☐ 每个市场使用统一 URL 策略 | 只选一种：子目录 **或** 子域名 **或** 国家域名，不混用 | 抽查 2–3 个市场的产品 URL 格式一致 |
| ☐ 语言与市场对应正确 | 如 en-US、de-DE、fr-FR、zh-CN 等 | 前台切换语言/地区，URL 与内容匹配 |
| ☐ 主市场与主语言明确 | 默认语言即主站语言，对应主域名或根路径 | 根路径 `/` 与主市场一致 |
| ☐ 无「仅 IP 跳转」导致爬虫只看到一种语言 | 不要仅凭 IP 强制跳转，保留按 URL 可访问各语言 | 用无痕/换地区 VPN 直接访问 `/de/`、`/fr/` 等可打开 |

**注意**：新市场默认可能不再自动带子文件夹，需在 Markets 里为每个市场明确配置「域名或子目录/子域名」。

---

### 2. Hreflang 与 Canonical

**Shopify**：使用 **Markets + 多语言** 时，会为各语言/市场生成不同 URL，并**自动输出** hreflang；需确认实现是否符合最佳实践。

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 每页存在 hreflang 标签 | 所有语言/地区版本在 `<head>` 中有 `rel="alternate" hreflang="xx-XX" href="..."` | 查看产品页/首页源码，搜索 `hreflang` |
| ☐ 包含自引用 | 当前页的 hreflang 中有一条指向当前页 URL | 当前页 URL 出现在同一组 hreflang 的 href 中 |
| ☐ 成对互链 | A 指向 B，B 也指向 A；无单向或缺失 | 用 GSC「网页」或第三方 hreflang 检查工具 |
| ☐ 语言/国家代码正确 | 如 `en-US`、`de-DE`、`zh-CN`（ISO 639-1 + ISO 3166-1） | 检查 hreflang 属性值，不用 `eu` 等非标准 |
| ☐ 每页 canonical 为自引用 | `<link rel="canonical" href="当前页完整 URL">`，不指向其他语言 | 查看源码 `rel="canonical"` |
| ☐ 无「全站统一 canonical 到首页」错误 | 不能所有语言页都 canonical 到主站首页 | 每页 canonical = 该页自己的 URL |

**若主题/App 未正确输出**：用主题 Liquid 在 `theme.liquid` 的 `<head>` 中按 Shopify 官方建议输出 hreflang + canonical，或使用合规的 hreflang/多语言 App 并验证输出。

---

### 3. 多语言 Sitemap 与 GSC

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 已提交主 sitemap | 通常 `https://你的域名/sitemap.xml` | GSC → 站点地图，已提交且无错误 |
| ☐ 各语言/市场 URL 可被收录 | sitemap 中包含各语言产品/分类 URL，或单独 sitemap 按语言 | 在 sitemap 中搜索 `/de/`、`/fr/` 等是否有对应 URL |
| ☐ GSC 已添加该域名（含主域） | 以主域为属性 | GSC 中可看到该网站 |
| ☐ 定期查看「覆盖率 / 网页」 | 关注「已编入索引」与错误（重复、缺失 hreflang 等） | GSC 报告无大量异常 |

---

### 4. 产品页结构化数据（Product JSON-LD）

**目的**：传统搜索富摘要 + GEO/AI 解析商品信息。

**实现**：主题内用 Liquid 在 `product.liquid` 或 `sections/` 中输出 JSON-LD，或使用可注入 Product schema 的 App。

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 每产品页有且仅有一组 Product 类型的 JSON-LD | 在 `<script type="application/ld+json">` 中 | 查看产品页源码，搜索 `application/ld+json` |
| ☐ 包含：name, image, description, sku, brand, offers | offers 含 price、priceCurrency、availability、url | Google 富媒体测试工具 无错误 |
| ☐ 价格/货币与当前市场一致 | 多市场时 schema 中的 priceCurrency 与页面展示一致 | 切换市场后刷新，用富媒体测试或查看 JSON-LD |
| ☐ 库存状态准确 | availability 为 InStock/OutOfStock 等 | 有货/缺货产品各测一页 |
| ☐ 若有评分，使用 AggregateRating | 与页面展示一致 | 富媒体测试中可识别评分 |

**可选**：BreadcrumbList 便于搜索与 AI 理解层级。

---

## 三、P1：短期必做（内容与体验）

### 5. 标题、描述、URL 与本地化内容

**后台**：产品/系列/页面 → 编辑 → SEO 与「翻译并调整」等。

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 每语言有独立 title/description | 不依赖机翻默认值，核心市场人工审校 | 切换语言查看标题与 meta description |
| ☐ 标题长度约 50–60 字符 | 避免过长被截断 | 各语言抽查若干页 |
| ☐ Meta description 约 120–160 字符 | 自然融入卖点与本地关键词 | 同上 |
| ☐ URL slug 简短且含关键词 | 产品/集合 handle 简洁可读 | 查看前台 URL |
| ☐ 核心市场非机翻 | 至少主市场 + 1–2 个重点市场为人工翻译/撰写 | 内容与本地表达一致 |
| ☐ 货币、单位、尺码表本地化 | 各市场使用当地货币与单位 | 结账页与产品页展示正确 |

---

### 6. 自引用 Canonical 与 Hreflang 互链（再次验证）

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 任意语言产品页 canonical 指向自身 | 无指向其他语言或首页 | 每语言抽 1 个产品页查源码 |
| ☐ GSC 无 hreflang 相关警告 | 无「未双向链接」等提示 | GSC → 设置 → 国际定位（若仍有）或第三方工具 |

---

### 7. Core Web Vitals 与移动端

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ LCP、INP/FID、CLS 达标 | 绿色为佳 | PageSpeed Insights 或 GSC「核心网页指标」 |
| ☐ 移动端单独测 | 多语言/多地区各抽 1–2 页 | 同上，选移动设备 |
| ☐ 图片懒加载与合适尺寸 | 主题或 App 已优化图片 | 大图有 srcset 或合适 max 宽度 |
| ☐ 使用 CDN | 如 Shopify CDN 或 Cloudflare | 不同地区测速可接受 |

---

## 四、P2：中期做（GEO 与长期权威）

### 8. FAQ / Article 等 Schema（利于 GEO）

**目的**：让 AI 与 AEO/GEO 更好理解问答与文章内容，便于引用。

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 重要 FAQ 页面有 FAQPage JSON-LD | 退换货、配送、支付等 | 富媒体测试识别 FAQ |
| ☐ 博客/文章有 Article 或 NewsArticle | 若有内容营销 | 同上 |
| ☐ 每页仅一种主要 schema 类型 | 不混用冲突类型 | 无富媒体错误/警告 |

**实现**：主题 Liquid 在对应模板（如 `page.liquid`、文章模板）或用 App 注入。

---

### 9. llms.txt 或 AI 抓取策略（可选）

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 已决定是否允许 AI 抓取 | 若允许，可提供说明与入口 | 文档或 meta 一致 |
| ☐ 若使用 llms.txt | 放在站根或约定路径，说明站点用途与规则 | 访问 `https://你的域名/llms.txt` 可读 |

**实现**：通过主题添加静态页或 App；Shopify 无官方 llms.txt，需自行挂载。

---

### 10. 本地外链与引用监测

| 检查项 | 说明 | 如何验证 |
|--------|------|----------|
| ☐ 重点市场有本地外链 | 当地媒体、测评、KOL | 用 Ahrefs/SEMrush 等看反向链接国家分布 |
| ☐ 定期在 AI 中查品牌/产品被引用 | 在 ChatGPT、Perplexity、Google SGE 搜品牌名+产品类目 | 记录是否被引用、描述是否准确 |
| ☐ 重要页面 E-E-A-T 可见 | 关于我们、联系、退换政策、认证等清晰 | 人工浏览 + 结构化数据完整 |

---

## 五、按阶段执行顺序建议

```
第 1 周（P0）
├── 配置 Markets + 语言 + 域名/子目录策略
├── 验证 hreflang + canonical 自动输出或补全
├── 提交 sitemap、加 GSC
└── 产品页 Product JSON-LD 上线并验证

第 2–3 周（P1）
├── 核心市场标题/描述/内容本地化
├── 再次全站抽查 canonical / hreflang
└── Core Web Vitals 检测与修复

第 4 周及以后（P2）
├── FAQ/Article schema
├── 可选 llms.txt
└── 外链与 AI 引用监测（每月至少 1 次）
```

---

## 六、Shopify 后台快速对照

| 功能 | 大致位置 |
|------|----------|
| 市场与域名 | 设置 → 市场 → 各市场 → 域名与 URL |
| 语言 | 设置 → 语言 / 或通过「翻译并调整」App |
| 产品 SEO | 产品 → 编辑 → SEO 与翻译 |
| 主题代码 | 在线商店 → 主题 → 编辑代码 |
| Sitemap | 自动：`/sitemap.xml`，GSC 中提交 |

---

## 七、验收清单（上线前打勾）

- [ ] 至少 2 个语言/市场，URL 结构统一且可访问
- [ ] 任意产品页：hreflang 含自引用 + 成对互链，canonical 自引用
- [ ] GSC 已提交 sitemap，无严重覆盖错误
- [ ] 产品页通过富媒体测试（Product），无错误
- [ ] 主市场 + 1 个非主语言：title/description 已本地化
- [ ] 移动端 Core Web Vitals 至少为「良好」或可接受

完成 P0+P1 后，再按节奏补 P2（FAQ schema、llms.txt、外链与 AI 监测）。若你提供当前主题名称或是否使用多语言 App，可再细化到具体 Liquid 或 App 配置步骤。
