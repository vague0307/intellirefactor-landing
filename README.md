# intellirefactor.com — 智慧重构

域名出售单页。`intelligent + refactor = 智慧重构`，主视觉是一次真实的代码重构 diff 动画：遗留代码逐行删去，AI 重构后的清晰代码逐行亮起。

- 纯静态（HTML/CSS/JS，零依赖零构建），字体自托管（JetBrains Mono / Instrument Sans 变量字体，~60KB）
- 询价表单合成 mailto 邮件发送至 **vague0307@gmail.com**（无第三方表单服务依赖）
- 尊重 `prefers-reduced-motion`；移动端适配；键盘可达

## 本地预览

```bash
python3 -m http.server 8923
# 打开 http://127.0.0.1:8923/
```

## 线上部署（阿里云 ECS）

- 服务器：与 nxerp / motowiki 同一台 ECS，nginx 由宝塔面板管理
- 站点根目录：`/opt/intellirefactor`（本仓库 clone），nginx vhost：`/www/server/panel/vhost/nginx/intellirefactor.conf`
- 推送到 main 自动部署：GitHub Actions 通过 SSH 拉取最新代码（见 `.github/workflows/deploy.yml`，secrets：`ECS_HOST` / `ECS_USER` / `ECS_SSH_PRIVATE_KEY`）

## 文件结构

```
index.html            页面主体（含完整 diff 静态标记，noscript 可读）
assets/styles.css     设计系统：diff 三色（删除红/新增绿/智能琥珀）
assets/main.js        diff 逐行动画 · 询价邮件合成 · 复制邮箱
assets/favicon.svg    站点图标
assets/fonts/         自托管变量字体
```
