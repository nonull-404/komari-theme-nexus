# Komari Nexus 二开说明

本仓库 fork 自 [Tokinx/komari-theme-emerald](https://github.com/Tokinx/komari-theme-emerald)（MIT），是 NexusDock 设备群监控面板 `https://komari.970407.xyz` 使用的前台主题。后端保持官方 Komari 不改，以便跟随上游升级。

## 分支

| 分支 | 用途 |
|---|---|
| `master` | 跟上游保持一致，只做同步，不在这里改 |
| `nexus` | 我们的改动都在这里 |

## 本地开发

```bash
bun install
# 开发时把接口代理到线上面板（只读数据，不需要登录）
bun run dev
bun run lint
bun run build      # 类型检查 + 构建，产出 komari-theme-nexus-build-<sha>.zip
```

## 发布到面板

在 O1 上执行（会自动构建、上传、切换为当前主题）：

```bash
~/src/komari-theme-nexus/scripts/deploy-nexus.sh
```

或者手动：后台 → 设置 → 主题管理 → 上传主题 → 选择 zip。

## 同步上游

```bash
git fetch upstream
git checkout master && git merge --ff-only upstream/master && git push origin master
git checkout nexus && git merge master   # 解决冲突后 bun run build 验证
```

## 已做的改动

- 主题标识改为 `Nexus`（short），与上游 `Emerald` 可以并存，互不覆盖
- 产物命名 `komari-theme-nexus-build-<sha>.zip`
- 页脚链接指向本仓库；浏览器缓存键改为 `komari-theme-nexus:*`，不与上游主题串数据

## 代码入口

- `src/views/HomeView.vue` 首页（卡片 / 列表视图）
- `src/views/InstanceDetail.vue` 节点详情
- `src/components/` 界面组件；`src/utils/rpc.ts` 数据接口（说明见 `src/utils/rpc.md`）
- `komari-theme.json` 后台可配置项（改完需重新上传主题）
