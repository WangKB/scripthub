# Dreamina Image Generator

一个使用字节跳动火山引擎即梦AI API生成图片的Python命令行工具。

## 功能特性

- 文生图：通过文本提示词生成图片
- 图生图：支持参考图片（本地文件或URL）
- 自定义尺寸：支持设置图片宽度和高度
- 可复现性：可设置随机种子复现相同结果
- 高级参数：支持提示词相关性、迭代步数等参数
- SDK封装：使用官方volcengine SDK，自动处理签名认证
- 自动下载：生成完成后自动下载图片到指定路径

## 前置要求

- Python 3.7+
- 火山引擎账号，并开通即梦AI服务
- 从火山引擎控制台获取 Access Key (AK) 和 Secret Key (SK)

## 安装

```bash
# 克隆仓库
git clone https://github.com/WangKB/scripthub.git
cd scripthub

# 安装依赖（使用uv更快）
uv pip install volcengine

# 或使用传统pip
pip install volcengine
```

## 使用方法

### 设置环境变量

**Windows (PowerShell):**
```powershell
$env:VOLCENGINE_AK="your-access-key"
$env:VOLCENGINE_SK="your-secret-key"
```

**Linux/Mac (Bash):**
```bash
export VOLCENGINE_AK="your-access-key"
export VOLCENGINE_SK="your-secret-key"
```

### 基本使用

```bash
# 最简单的文生图
python dreamina_gen.py -p "一只可爱的猫咪" -o cat.jpg

# 自定义尺寸
python dreamina_gen.py -p "未来城市风景" -o city.jpg --width 2048 --height 1024

# 使用随机种子（可复现）
python dreamina_gen.py -p "抽象艺术" -o art.jpg --seed 12345
```

### 命令行参数

```
必需参数:
  -p, --prompt PROMPT       生成图片的文本提示词
  -o, --output OUTPUT       输出图片的文件路径

可选参数:
  -h, --help                显示帮助信息
  --req-key REQ_KEY         模型版本标识 (默认: high_aes_general_v21_L 即图片生成4.0)
  --width WIDTH             图片宽度，单位像素 (默认: 1024)
  --height HEIGHT           图片高度，单位像素 (默认: 1024)
  --seed SEED               随机种子，用于复现相同结果
  --scale SCALE             提示词相关性，控制生成结果与提示词的贴合度
  --ddim-steps DDIM_STEPS   迭代步数，影响生成质量和速度
  --logo                    添加logo水印
  --ref-images IMAGE [IMAGE ...]
                            参考图片的本地文件路径，支持多张
  --ref-urls URL [URL ...]  参考图片的URL地址，支持多个
```

### 使用示例

#### 1. 基础文生图
```bash
python dreamina_gen.py -p "一只戴眼镜的可爱猫咪" -o cat.jpg
```

#### 2. 自定义图片尺寸
```bash
# 生成2K分辨率图片
python dreamina_gen.py -p "壮丽的山脉日落" -o sunset.jpg --width 2048 --height 2048

# 生成宽屏图片
python dreamina_gen.py -p "海滩全景" -o beach.jpg --width 2048 --height 1024
```

#### 3. 使用参考图片（图生图）
```bash
# 使用本地图片作为参考
python dreamina_gen.py -p "相似风格的风景画" -o landscape.jpg --ref-images style.jpg

# 使用多张参考图片
python dreamina_gen.py -p "混合这些风格" -o mixed.jpg --ref-images ref1.jpg ref2.jpg ref3.jpg

# 使用URL作为参考图
python dreamina_gen.py -p "类似风格" -o output.jpg --ref-urls "https://example.com/image.jpg"

# 同时使用本地图片和URL
python dreamina_gen.py -p "融合风格" -o result.jpg \
  --ref-images local.jpg \
  --ref-urls "https://example.com/style.jpg"
```

#### 4. 高级参数控制
```bash
# 使用随机种子确保可复现
python dreamina_gen.py -p "抽象艺术" -o art.jpg --seed 42

# 调整提示词相关性
python dreamina_gen.py -p "梦幻森林" -o forest.jpg --scale 7.5

# 设置迭代步数（更多步数通常质量更好但速度更慢）
python dreamina_gen.py -p "精细的人物肖像" -o portrait.jpg --ddim-steps 50

# 添加水印
python dreamina_gen.py -p "商业用图" -o commercial.jpg --logo
```

#### 5. 组合使用
```bash
# 综合使用多个参数
python dreamina_gen.py \
  -p "赛博朋克风格的未来城市，霓虹灯闪烁" \
  -o cyberpunk.jpg \
  --width 2048 \
  --height 1024 \
  --seed 999 \
  --scale 8.0 \
  --ref-images cyberpunk_style.jpg
```

## API参考文档

本工具使用以下火山引擎API：

- [即梦AI-图片生成4.0 接口文档](https://www.volcengine.com/docs/85621/1817045)
- [即梦AI-图片生成4.0 产品介绍](https://www.volcengine.com/docs/85621/1820192)
- [火山引擎 Visual SDK](https://github.com/volcengine/volcengine-python-sdk)

## 技术实现

- 使用官方 `volcengine-python-sdk` 的 `VisualService` 模块
- SDK自动处理API签名认证（HMAC-SHA256）
- 支持环境变量配置AK/SK，确保凭证安全
- 自动处理图片下载和保存

## 注意事项

1. **环境变量必须设置**：脚本依赖 `VOLCENGINE_AK` 和 `VOLCENGINE_SK` 环境变量
2. **费用说明**：使用即梦AI API会产生费用，请查看[计费说明](https://www.volcengine.com/docs/85621/1544714)
3. **图片尺寸**：支持的尺寸范围请参考官方文档，推荐使用1024x1024或2048x2048
4. **生成时间**：通常2K分辨率图片生成时间约1.8-8秒，具体取决于服务器负载

## 常见问题

**Q: 提示"请设置环境变量"怎么办？**  
A: 请按照上面的说明设置 `VOLCENGINE_AK` 和 `VOLCENGINE_SK` 环境变量。

**Q: 生成的图片质量不满意？**  
A: 可以尝试调整 `--ddim-steps` 参数（增加迭代步数）或使用 `--ref-images` 提供参考图片。

**Q: 如何让生成结果更接近提示词？**  
A: 增加 `--scale` 参数值（如 `--scale 8.0`），这会让生成结果更贴合提示词。

**Q: 支持哪些图片格式？**  
A: 输出支持常见图片格式（jpg, png等），由你指定的输出文件扩展名决定。

## 许可证

MIT License - 可自由使用和修改。
