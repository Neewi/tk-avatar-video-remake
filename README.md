# TK 数字人视频

运营看图选择数字人与造型，用自家产品复刻参考视频，默认得到一张关键帧宫格和一条完整 Symphony 音视频提示词。

## 使用

1. 克隆本仓库，并在 Codex 中打开项目文件夹。
2. 安装 Python 3 和 Pillow，可运行 `python3 -m pip install -r requirements.txt`。视频解析需要 FFmpeg/FFprobe，人物和宫格制作需要可用的图像生成工具。
3. 对 Codex 说“按本项目的 skill，帮我复刻这条视频”，附上视频即可。也可以说“创建一个数字人”或“给小夏换一套健身装”。
4. 也可把 `skill/avatar-video-remake` 复制到个人 skills 目录，通过 `$avatar-video-remake` 调用，使用时仍打开本项目。项目配置按当前项目定位，支持命令行 `--project` 指定根目录。

首次使用时引导创建人物、预览和命名。参考人物图会先提炼成文字，再重新设计虚构人物。已有数字人时展示实际图片选择，所选脸、发型和衣服沿用到视频。新造型存到同一人物名下。

## 目录与共享

| 路径 | 内容 | Git |
|---|---|---|
| skill/avatar-video-remake/ | skill 说明和辅助脚本 | 同步 |
| assets/products/ | 9 个型号的产品图及配件，默认 T10P | 同步 |
| workspace/people/ | 已确认人物及造型，每套四图和 look.json | 同步 |
| workspace/runs/ | 原视频、人物草稿、分析帧、宫格、提示词和任务记录 | 忽略 |
| avatar-remake.json | 相对路径和生成配置 | 同步 |

选人前会拉取项目更新，新人物或造型保存后按 skill 指引提交并推送。运营需要拥有本仓库的推送权限和本机 Git 登录。共享依赖成功的推送与拉取，遇到网络或合并问题会保留本地成果并说明未同步。人物库起初为空。

可手动同步已保存人物：

```sh
git pull --ff-only
git add workspace/people/
git commit -m "Add avatar look"
git push
```

产品资料来自本项目素材。T10P、TB02、TAB10 附有现有核对资料，其他型号目前以图片定义外观，具体参数、价格、功能与活动需要运营提供或确认。

生成时长目前配置为 15 秒，可在 avatar-remake.json 中调整。超长参考视频会先让运营选择保留片段。视频模型的实际输入支持和生成效果需按使用入口验证。
