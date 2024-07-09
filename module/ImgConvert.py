import os

from PIL import Image, ImageDraw, ImageFont
import random
from typing import Tuple, List
from module.config import Config


def textsize(draw: ImageDraw, content: str, font: ImageFont) -> Tuple[int, int]:
    _, _, width, height = draw.textbbox((0, 0), content, font=font)
    return width, height


class Color:
    def __init__(self, hex_color: str):
        self.hex_color = hex_color
        self.rgb = tuple(int(hex_color[1 + i:1 + i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def from_hex(hex_color: str) -> 'Color':
        return Color(hex_color)

    def __repr__(self):
        return f"Color(Hex={self.hex_color}, RGB={self.rgb})"


class StyledString:
    def __init__(self, config: Config, content: str, font_type: str, font_size: int,
                 font_color: Tuple[int, ...] = (0, 0, 0), line_multiplier=1.0):  # 添加字体颜色
        file_path = os.path.join(config.work_dir, config.get_config('data'), f'OPPOSans-{font_type}.ttf')
        self.content = content
        self.font_color = font_color
        self.line_multiplier = line_multiplier
        # 尝试加载字体
        try:
            self.font = ImageFont.truetype(file_path, font_size)
        except IOError:
            raise IOError(f"无法加载字体文件: {file_path}")
        self.height = ImgConvert.calculate_string_height(file_path, font_size, content, line_multiplier=line_multiplier)


class ImgConvert:
    MAX_WIDTH = 1024

    """  
    计算文本在给定字体和大小下的长度（宽度）。  
  
    :param font_type: 字体文件 
    :param font_size: 字体大小  
    :param content: 要测量的文本内容  
    :return: 文本的宽度（像素）  
    """

    @staticmethod
    def calculate_string_width(font_type, font_size, content):

        try:
            # 加载字体  
            font = ImageFont.truetype(font_type, font_size)
        except IOError:
            print(f"无法加载字体文件: {font_type}")
            return 0

            # 创建一个虚拟图像，该图像足够大以绘制文本
        image = Image.new('RGB', (ImgConvert.MAX_WIDTH, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 获取文本的宽度（不实际显示图像）  
        text_width, text_height = textsize(draw, content, font=font)

        # 返回文本的宽度  
        return text_width

    """  
    计算文本在给定字体和大小下的高度。  
  
    :param font_type:       字体文件 
    :param font_size:       字体大小  
    :param content:         要测量的文本内容  
    :param max_width:       文本最大长度
    :param line_multiplier  行距
    :return:                文本的高度
    """

    @staticmethod
    def calculate_string_height(font_type, font_size, content, max_width=MAX_WIDTH, line_multiplier=1.0):
        # 加载字体
        font = ImageFont.truetype(font_type, font_size)
        # font = "symbol.ttf"

        # 创建一个足够大的图像来绘制文本（这里只是一个临时图像）
        temp_image = Image.new('RGB', (max_width * 2, 1000), color=(255, 255, 255))
        draw = ImageDraw.Draw(temp_image)

        x, y = 0, 0
        line_height = font.getbbox('A')[3]  # 使用'A'的高度作为行高，这通常是一个合理的近似值

        words = content.split()
        line = []

        for word in words:
            # 尝试将单词添加到当前行
            test_width, _ = textsize(draw, content, font=font)

            if test_width <= max_width:
                line.append(word)
            else:
                # 如果当前行太宽，则绘制它并开始新行  
                draw.text((x, y), ' '.join(line), font=font, fill=(0, 0, 0))
                y += line_height * line_multiplier
                line = [word]

                # 绘制最后一行
        draw.text((x, y), ' '.join(line), font=font, fill=(0, 0, 0))
        total_height = y + line_height * line_multiplier  # 确保总高度包括最后一行  

        del temp_image

        return int(total_height)

    """  
    绘制文本
  
    :param draw             目标图层
    :param styled_string    包装后的文本内容
    :param x                文本左上角的横坐标 
    :param y                文本左上角的纵坐标
    :param max_width        文本最大长度
    :param line_multiplier  行距
    """

    @staticmethod
    def draw_string(draw: ImageDraw, styled_string: StyledString, x, y, max_width=MAX_WIDTH):
        offset = 0
        lines = styled_string.content.split("\n")

        for line in lines:
            if not line.strip():  # 忽略空行  
                offset += int(styled_string.font.getbbox('A')[3] * styled_string.line_multiplier)
                continue

            text_width, text_height = textsize(draw, line, font=styled_string.font)
            temp_text = line

            while text_width > max_width:
                # 简单的文本分割逻辑，考虑是不是需要更复杂的分割逻辑
                n = text_width // max_width
                sub_pos = len(temp_text) // n
                draw_text = temp_text[:sub_pos]
                draw_width, _ = textsize(draw, draw_text, font=styled_string.font)

                while draw_width > max_width and sub_pos > 0:
                    sub_pos -= 1
                    draw_text = temp_text[:sub_pos]
                    draw_width, _ = textsize(draw, draw_text, font=styled_string.font)

                draw.text((x, y + offset), draw_text, font=styled_string.font, fill=styled_string.font_color)
                offset += int(text_height * styled_string.line_multiplier)
                temp_text = temp_text[sub_pos:]
                text_width -= draw_width
            draw.text((x, y + offset), temp_text, font=styled_string.font, fill=styled_string.font_color)
            offset += int(text_height * styled_string.line_multiplier)

    """  
    给图片应用覆盖色
  
    :param image        目标图片
    :param tint         覆盖色
    :return             处理完后的图片
    """

    @staticmethod
    def apply_tint(image_path:str, tint: tuple[int, int, int]):
        r,g,b = tint
        image = Image.open(image_path)
        width, height = image.size
        tinted_image = Image.new("RGBA", (width, height), color=tint+ (255,))
        alpha = 0.5
        for x in range(width):
            for y in range(height):
                orig_pixel = image.getpixel((x, y))
                mixed_r = int(orig_pixel[0] * (1 - alpha) + r * alpha)
                mixed_g = int(orig_pixel[1] * (1 - alpha) + g * alpha)
                mixed_b = int(orig_pixel[2] * (1 - alpha) + b * alpha)
                tinted_image.putpixel((x, y), (mixed_r, mixed_g, mixed_b, orig_pixel[3]))
        return tinted_image

    class GradientColors:
        colors = [
            ["#C6FFDD", "#FBD786", "#f7797d"],
            ["#009FFF", "#ec2F4B"],
            ["#22c1c3", "#fdbb2d"],
            ["#3A1C71", "#D76D77", "#FFAF7B"],
            ["#00c3ff", "#ffff1c"],
            ["#FEAC5E", "#C779D0", "#4BC0C8"],
            ["#C9FFBF", "#FFAFBD"],
            ["#FC354C", "#0ABFBC"],
            ["#355C7D", "#6C5B7B", "#C06C84"],
            ["#00F260", "#0575E6"],
            ["#FC354C", "#0ABFBC"],
            ["#833ab4", "#fd1d1d", "#fcb045"],
            ["#FC466B", "#3F5EFB"]
        ]

        @staticmethod
        def generate_gradient() -> tuple[list[str], list[float]]:
            now_colors = ImgConvert.GradientColors.colors[random.randint(0, len(ImgConvert.GradientColors.colors) - 1)]
            if random.randint(0, 1):
                now_colors.reverse()
            colors_list = [color for color in now_colors]
            position_list = [0.0, 1.0] if len(now_colors) == 2 else [0.0, 0.5, 1.0]
            return colors_list, position_list
