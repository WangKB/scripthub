#!/usr/bin/env python3
import os
import argparse
import base64
import requests
from volcengine.visual.VisualService import VisualService

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prompt', required=True, help='生成图片的文本提示词')
    parser.add_argument('-o', '--output', required=True, help='输出图片的文件路径')
    parser.add_argument('--req-key', default='high_aes_general_v21_L', help='模型版本标识，默认为图片生成4.0')
    parser.add_argument('--width', type=int, default=1024, help='图片宽度，默认1024')
    parser.add_argument('--height', type=int, default=1024, help='图片高度，默认1024')
    parser.add_argument('--seed', type=int, help='随机种子，用于复现相同结果')
    parser.add_argument('--scale', type=float, help='提示词相关性，控制生成结果与提示词的贴合度')
    parser.add_argument('--ddim-steps', type=int, help='迭代步数，影响生成质量和速度')
    parser.add_argument('--logo', action='store_true', help='是否添加logo水印')
    parser.add_argument('--ref-images', nargs='+', help='参考图片路径，支持多张图片')
    parser.add_argument('--ref-urls', nargs='+', help='参考图片URL，支持多个URL')
    args = parser.parse_args()
    
    # 初始化服务
    visual_service = VisualService()
    
    # 从环境变量获取AK/SK
    ak = os.environ.get('VOLCENGINE_AK')
    sk = os.environ.get('VOLCENGINE_SK')
    
    if not ak or not sk:
        print("错误: 请设置环境变量 VOLCENGINE_AK 和 VOLCENGINE_SK")
        print("设置方法:")
        print("  Windows (PowerShell): $env:VOLCENGINE_AK='your-ak'; $env:VOLCENGINE_SK='your-sk'")
        print("  Linux/Mac: export VOLCENGINE_AK='your-ak'; export VOLCENGINE_SK='your-sk'")
        return
    
    visual_service.set_ak(ak)
    visual_service.set_sk(sk)
    
    # 构建请求参数
    form = {
        "req_key": args.req_key,
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
        "return_url": True,
        "logo_info": {
            "add_logo": args.logo
        }
    }
    
    # 添加可选参数
    if args.seed is not None:
        form["seed"] = args.seed
    
    if args.scale is not None:
        form["scale"] = args.scale
    
    if args.ddim_steps is not None:
        form["ddim_steps"] = args.ddim_steps
    
    # 处理参考图片
    image_urls = []
    binary_data_base64 = []
    
    # 从本地文件读取图片并转为base64
    if args.ref_images:
        for img_path in args.ref_images:
            with open(img_path, 'rb') as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                binary_data_base64.append(img_base64)
        print(f"已加载 {len(args.ref_images)} 张本地参考图片")
    
    # 使用URL形式的参考图
    if args.ref_urls:
        image_urls.extend(args.ref_urls)
        print(f"已添加 {len(args.ref_urls)} 个参考图片URL")
    
    # 将参考图添加到请求中
    if binary_data_base64:
        form["binary_data_base64"] = binary_data_base64
    
    if image_urls:
        form["image_urls"] = image_urls
    
    # 调用CV处理接口
    print(f"正在生成图片: {args.prompt}")
    resp = visual_service.cv_process(form)
    
    # 处理响应
    if "data" in resp and "image_urls" in resp["data"] and len(resp["data"]["image_urls"]) > 0:
        image_url = resp["data"]["image_urls"][0]
        print(f"图片生成成功，正在下载...")
        
        # 直接下载图片内容
        response = requests.get(image_url, timeout=60)
        
        # 保存到文件
        with open(args.output, 'wb') as f:
            f.write(response.content)
        
        # 验证文件大小
        file_size = os.path.getsize(args.output)
        print(f"图片已保存到: {args.output} (大小: {file_size:,} bytes)")
    else:
        print("生成失败，响应内容:")
        import json
        print(json.dumps(resp, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
