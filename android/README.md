# Android 项目 - 本地无需 Android Studio

## 核心特性

- ❌ **不需要安装 Android Studio**
- ❌ **不需要下载 Android SDK**
- ❌ **不需要本地编译 APK**
- ✅ **GitHub Actions 自动在线构建**

---

## 项目结构

```
android/
├── android/                          ← Android 原生项目
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/localrest/mobile/
│   │   │   │   ├── MainActivity.kt    ← 主Activity (WebView)
│   │   │   │   ├── ApiBridge.kt       ← JS-Kotlin桥接
│   │   │   │   └── DatabaseHelper.kt  ← SQLite操作
│   │   │   ├── res/                   ← 资源文件
│   │   │   └── AndroidManifest.xml
│   │   ├── build.gradle
│   │   └── proguard-rules.pro
│   ├── build.gradle
│   ├── settings.gradle
│   └── gradle.properties
├── web/                               ← H5页面
│   ├── index.html
│   └── js/
├── assets/                            ← 数据文件
│   └── sampleData.json
├── scripts/                           ← 签名工具
│   ├── generate-keystore.bat
│   └── export-keystore-base64.bat
└── README.md
```

---

## 您本地需要做的

### 1. 写 Android 代码（用您熟悉的 Java/Kotlin）

在 `android/android/app/src/main/` 目录下修改代码。

### 2. 写 H5 页面（可选）

在 `android/web/` 目录下修改 H5 页面。

### 3. 准备数据

- **方式一**：将 `data/localrest.db` 放到项目根目录
- **方式二**：将 `android/assets/sampleData.json` 替换为您的数据

### 4. 推送代码到 GitHub

```bash
git add .
git commit -m "feat: 更新 Android 代码"
git push origin main
```

---

## 在线构建（自动）

每次推送代码后，GitHub Actions 会自动：

1. ✅ 安装 Java 17
2. ✅ 安装 Gradle 8.7
3. ✅ 安装 Android SDK
4. ✅ 编译项目
5. ✅ 生成 APK
6. ✅ 上传 Artifacts 供下载

---

## 下载 APK

### 方式一：查看构建日志

1. 进入 GitHub 仓库 → **Actions**
2. 选择最新的 **Build Android APK** 构建
3. 查看构建日志

### 方式二：下载 Artifacts

1. 构建完成后，在构建页面底部的 **Artifacts** 区域
2. 点击 **app-debug** 下载 ZIP
3. 解压后得到 APK
4. 安装到手机

---

## 触发构建

### 自动触发
- 推送到 `main`、`master`、`develop` 分支时自动构建

### 手动触发
1. GitHub 仓库 → **Actions** → **Build Android APK**
2. 点击 **Run workflow**
3. 选择构建类型：
   - `debug`：调试版本（无需签名，可直接安装）
   - `release`：发布版本（需要配置签名）
4. 点击 **Run workflow**

---

## Release 版本签名（可选）

如果需要发布到应用商店，需要配置签名密钥。

### 1. 生成签名密钥

```bash
cd android/scripts
generate-keystore.bat
export-keystore-base64.bat
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**：

| Secret | 值 |
|--------|-----|
| `KEYSTORE_FILE` | keystore-base64.txt 的内容 |
| `KEYSTORE_PASSWORD` | `localrest123` |
| `KEY_ALIAS` | `localrest` |
| `KEY_PASSWORD` | `localrest123` |

### 3. 手动触发 Release 构建

选择 `release` 类型触发构建。

---

## 技术栈

| 组件 | 版本 |
|------|------|
| Java | 17 |
| Gradle | 8.7 |
| Android Gradle Plugin | 8.5.0 |
| Kotlin | 1.9.20 |
| compileSdk | 34 |
| minSdk | 24 (Android 7.0+) |
| targetSdk | 34 |

---

## 常见问题

### Q: 构建失败怎么办？

检查构建日志中的错误信息。常见问题：

1. **Gradle 版本问题**：检查 `gradle/wrapper/gradle-wrapper.properties`
2. **Android SDK 问题**：确保 `build.gradle` 中的版本匹配
3. **依赖问题**：检查 `app/build.gradle` 中的依赖

### Q: 如何修改应用名称？

修改 `app/src/main/res/values/strings.xml`：
```xml
<string name="app_name">您的应用名称</string>
```

### Q: 如何修改包名？

修改以下文件：
1. `app/build.gradle` - `applicationId`
2. `app/src/main/AndroidManifest.xml` - `package`
3. 目录结构：`java/com/localrest/mobile/` → 您的包名路径

### Q: 如何修改图标？

替换 `app/src/main/res/mipmap-*/` 目录下的图标文件。

---

## 下一步

1. 根据您的需求修改 Android 代码
2. 推送代码到 GitHub
3. 等待 GitHub Actions 自动构建
4. 下载 APK 测试
