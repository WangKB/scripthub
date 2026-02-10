# Dreamina Image Generator

A simple Python CLI tool for generating images using ByteDance Volcengine Dreamina AI API.

## Features

- Generate images from text prompts
- Support for custom image dimensions
- Configurable random seed for reproducibility
- Automatic HMAC-SHA256 authentication for Volcengine API
- Downloads and saves generated images to specified location

## Prerequisites

- Python 3.7+
- Volcengine account with Dreamina AI access
- Access Key (AK) and Secret Key (SK) from Volcengine console

## Installation

```bash
# Clone the repository
git clone https://github.com/WangKB/scripthub.git
cd scripthub

# No external dependencies required - uses only Python standard library
```

## Usage

### Set Environment Variables

```bash
export VOLCENGINE_AK="your-access-key"
export VOLCENGINE_SK="your-secret-key"
```

### Generate an Image

```bash
python dreamina_gen.py -p "a beautiful sunset over mountains" -o sunset.png
```

### Command Line Options

```
usage: dreamina_gen.py [-h] -p PROMPT -o OUTPUT [-W WIDTH] [-H HEIGHT] [-s SEED] [--ak AK] [--sk SK]

Generate images using ByteDance Volcengine Dreamina AI

required arguments:
  -p PROMPT, --prompt PROMPT
                        Text prompt describing the image to generate
  -o OUTPUT, --output OUTPUT
                        Output file path for the generated image

optional arguments:
  -h, --help            show this help message and exit
  -W WIDTH, --width WIDTH
                        Image width in pixels (default: 1024)
  -H HEIGHT, --height HEIGHT
                        Image height in pixels (default: 1024)
  -s SEED, --seed SEED  Random seed for reproducibility (optional)
  --ak AK               Access Key (or set VOLCENGINE_AK env var)
  --sk SK               Secret Key (or set VOLCENGINE_SK env var)
```

### Examples

```bash
# Basic usage with environment variables
python dreamina_gen.py -p "cute cat wearing glasses" -o cat.png

# Custom dimensions
python dreamina_gen.py -p "futuristic cityscape" -o city.png -W 1024 -H 768

# With specific seed for reproducibility
python dreamina_gen.py -p "abstract art" -o art.png -s 12345

# Pass credentials as arguments
python dreamina_gen.py -p "mountain landscape" -o mountain.png --ak YOUR_AK --sk YOUR_SK
```

## API Reference

This tool uses the following Volcengine APIs:

- [即梦AI-图片生成4.0 接口文档](https://www.volcengine.com/docs/85621/1817045)
- [HTTP请求示例](https://www.volcengine.com/docs/6444/1390583)
- [公共参数与签名方法](https://www.volcengine.com/docs/6369/67268)

## Authentication

The script implements the Volcengine API signature authentication (HMAC-SHA256) as documented in the official API guide. The signature is automatically generated for each request based on your AK/SK credentials.

## License

MIT License - feel free to use and modify as needed.
