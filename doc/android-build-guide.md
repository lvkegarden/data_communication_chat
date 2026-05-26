# Android APK 自动构建指南

## 目录
1. [项目结构
2. [前提条件
3. [快速开始](#快速开始)
4. [配置 GitHub Secrets](#配置-github-secrets)
5. [生成签名证书](#生成签名证书)
6. [触发构建](#触发构建)
7. [下载 APK](#下载-apk)
8. [常见问题](#常见问题)

---

## 1. 项目结构

```
localrest/
├── .github/
│   └── workflows/
│       └── build-android.yml      # GitHub Actions 工作流配置
├── android/
│   ├── package.json           # Capacitor 项目配置
│   ├── capacitor.config.json  # Capacitor 配置
│   ├── package.json        # 项目依赖
│   ├── init.bat          # 本地初始化脚本
│   ├── sync.bat          # 同步脚本
│   ├── scripts/
│   │   ├── generate-keystore.bat    # 生成签名证书
│   │   └── export-keystore-base64.bat  # 导出 Base64
│   ├── assets/
│   │   └── sampleData.json    # 示例数据
│   └── web/
│       ├── index.html       # 移动端 H5 页面
│       └── js/
│           └── dataService.js   # 数据服务层
└── data/
    └── localrest.db       # 产品数据库（自动打包）
```

---

## 2. 前提条件

### 本地开发（可选）
- Node.js 20+
- Java 17+
- （可选）Android Studio（如果需要本地调试）

### GitHub 构建（必需）
- GitHub 账号
- 项目已推送到 GitHub 仓库

---

## 3. 快速开始

### 步骤 1: 推送代码到 GitHub

```bash
git add .
git commit -m "Add Android build setup"
git push origin main
```

### 步骤 2: 配置 GitHub Secrets（Release 构建需要）

### 步骤 3: 触发构建（见下文）

---

## 4. 配置 GitHub Secrets

### 必需的 Secrets（Release 构建需要，Debug 不需要）

在 GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret

| Secret 名称 | 描述 |
|---------|------|
| `KEYSTORE_FILE` | Keystore 文件的 Base64 编码 |
| `KEYSTORE_PASSWORD` | Keystore 密码 |
| `KEY_ALIAS` | Key 别名 |
| `KEY_PASSWORD` | Key 密码 |

---

## 5. 生成签名证书

### 方法一：使用脚本（推荐）

1. 打开命令行，进入 `android/scripts/ 目录

2. 运行生成证书脚本：
```bash
cd android\scripts
generate-keystore.bat
```

3. 运行导出 Base64 脚本：
```bash
export-keystore-base64.bat
```

4. 打开生成的 `keystore-base64.txt`，复制内容（去掉首尾的分隔线）

### 方法二：使用 keytool 命令行

```bash
# 生成 keystore
keytool -genkeypair -v \
    -keystore localrest-release.keystore \
    -alias localrest \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass localrest123 \
    -keypass localrest123 \
    -dname "CN=LocalRest, OU=LocalRest, O=LocalRest, L=Local, ST=Local, C=CN"

# 转换为 Base64（Linux/Mac）
base64 localrest-release.keystore > keystore-base64.txt

# Windows）
certutil -encode localrest-release.keystore localrest-release.keystore-base64.txt
```

---

## 6. 触发构建

### 方式一：自动触发（推送代码时自动构建

当您推送到以下分支时自动构建 Debug APK：
- `main`
- `master`
- `develop`

### 方式二：手动触发（推荐）

1. 进入 GitHub 仓库 → Actions → Build Android APK

2. 点击 "Run workflow"

3. 选择构建类型：
   - `debug`：调试版本（无需签名）
   - `release`：发布版本（需要配置 Secrets）

4. 填写版本号（可选）

5. 点击 "Run workflow"

---

## 7. 下载 APK

构建完成后，在 Actions 页面查看：

1. 进入 GitHub 仓库 → Actions → 选择最新的构建 → Artifacts 部分

2. 下载：
   - `app-debug`：Debug 版本
   - `app-release`：Release 版本（如果配置了签名）

3. 下载 ZIP 文件，解压后即可获得 APK

4. 将 APK 传输到手机安装

---

## 8. 常见问题

### Q1: Debug 和 Release 有什么区别？

**Debug APK：
- 无需签名证书
- 可直接安装测试
- 包含调试信息
- 体积较大

**Release APK：
- 需要签名证书
- 体积较小
- 可以发布到应用商店
- 需要配置 GitHub Secrets

### Q2: 构建失败怎么办？

检查：
1. 查看 Actions 日志
2. 确保代码可以正常 `npm install`
3. 检查 Secrets 配置是否正确

### Q3: 如何更新数据？

将 `data/localrest.db` 放在项目根目录，构建时会自动复制到 APK 中。

如果没有这个文件，将使用 `android/assets/sampleData.json` 中的示例数据。

### Q4: 如何本地测试？

1. 初始化项目：
```bash
cd android
npm install
npx cap init
npx cap add android
npx cap sync
```

2. 在浏览器中打开 `android/web/index.html` 测试 H5 页面

### Q5: 如何修改应用名称和包名？

修改 `.github/workflows/build-android.yml` 中的环境变量：

```yaml
env:
  APP_NAME: 数通产品智能体
  PACKAGE_NAME: com.localrest.mobile
```

---

## 9. 构建流程说明

### GitHub Actions 工作流步骤：

```
1. Checkout 代码
   ↓
2. 安装 Node.js
   ↓
3. 安装 Java
   ↓
4. 安装 Android SDK
   ↓
5. npm install
   ↓
6. Capacitor 初始化
   ↓
7. 添加 Android 平台
   ↓
8. 复制数据库
   ↓
9. Capacitor Sync
   ↓
10. Gradle 构建 APK
   ↓
11. 上传 Artifacts
```

---

## 10. 版本历史

- v1.0.0 (2026-05-19)
  - 初始版本
  - 支持 GitHub Actions 自动构建
  - 支持 Debug 和 Release 构建
  - 支持自动签名
