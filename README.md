# intellirefactor.com — 智慧重构

域名出售单页。`intelligent + refactor = 智慧重构`，表达的不是狭义的代码重构，而是用 AI 重新设计组织的工作方式：重排人、AI、工具与数据，让流程从手工搬运升级为可以理解、执行和持续学习的 AI 原生工作流。

主视觉用三阶段动画解释这一定位：改造前的人工交接 → AI 对工作流的理解与重排 → 更少等待、持续优化的智能协作。

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
index.html            页面主体（含完整工作流静态标记，noscript 可读）
assets/styles.css     设计系统：工作流三色（阻塞红/生长绿/智能琥珀）
assets/main.js        工作流重构动画 · 询价邮件合成 · 复制邮箱
assets/favicon.svg    站点图标
assets/og.svg         OG 分享图可编辑源文件
assets/og.png         OG 分享图发布文件
assets/fonts/         自托管变量字体
tests/test_landing.py 定位与询价流程的静态回归测试
```

## 验证

```bash
python3 -B -m unittest tests/test_landing.py -v
node --check assets/main.js
```
