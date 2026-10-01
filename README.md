# json-shape

快速查看 JSON 的字段路径和数据类型；不会打印任何字段值，也不会联网。

## 使用

需要 Python 3.8+，不安装依赖。

```sh
python json_shape.py data.json
```

也可通过管道输入：

```sh
cat data.json | python json_shape.py
```

最多读取 8 MiB；摘要最多显示 5 层、20,000 个节点和 200 条结构记录，每个数组最多查看前 100 项、每个对象最多查看前 200 个字段。触及上限时会标明摘要不完整或使用了样本。超过 80 字符的对象字段名会缩写；对象字段名会显示，敏感字段名也可能包含在内。工具不会输出字段值。

## 许可

MIT，见 [LICENSE](LICENSE)。
## Linux x86_64 下载

- [单文件版](https://github.com/506058115-cmd/json-shape/releases/download/v1.0.0/json-shape-linux-x86_64-onefile.tar.gz)
- [目录版](https://github.com/506058115-cmd/json-shape/releases/download/v1.0.0/json-shape-linux-x86_64-onedir.tar.gz)
- [v1.0.0 Release 页面](https://github.com/506058115-cmd/json-shape/releases/tag/v1.0.0)

压缩包附带构建信息和依赖许可证；Release 另附 SHA-256 校验文件。产物在 WSL Ubuntu 24.04（Python 3.12.3、PyInstaller 6.22.2）中构建，目标为 GNU/Linux x86_64。较旧的发行版可能需要兼容的 glibc。
