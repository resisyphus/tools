import ebooklib
from ebooklib import epub
import re
import os

def txt_to_epub(txt_path, epub_path, title=None, author=None, cover_image=None):
    """
    将txt文件转换为epub电子书
    
    Args:
        txt_path: txt文件路径
        epub_path: 输出epub文件路径
        title: 书名
        author: 作者
        cover_image: 封面图片路径（可选）
    """
    book = epub.EpubBook()

    # 设置元数据
    book.set_identifier(f'id_{hash(txt_path)}')
    book.set_title(title or '未命名')
    book.set_language('zh-CN')
    if author:
        book.add_author(author)

    # 添加封面（如果提供了封面图片）
    if cover_image and os.path.exists(cover_image):
        try:
            with open(cover_image, 'rb') as img_file:
                book.set_cover("cover.jpg", img_file.read())
            print(f"✅ 已添加封面: {cover_image}")
        except Exception as e:
            print(f"❌ 添加封面失败: {e}")
    elif cover_image:
        print(f"❌ 封面图片不存在: {cover_image}")

    # 读取 txt 内容
    try:
        with open(txt_path, 'r', encoding='gbk') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

    # 分章处理
    chapter_pattern = re.compile(r'(第[\u4e00-\u9fa5\d]+章[^\n]*)\n(.*?(?=\n第[\u4e00-\u9fa5\d]+章|$))', re.DOTALL) # 匹配中文的章节标题和内容（比如“第一章外门弟子“）
    chapters = chapter_pattern.findall(content)
    
    if not chapters:
        chapters = [('正文', content)]

    chapter_objs = []
    for idx, (title_line, body) in enumerate(chapters):
        c_title = title_line.strip()
        c_content = body.strip()
        
        c = epub.EpubHtml(title=c_title, file_name=f'chap_{idx+1}.xhtml', lang='zh-CN')
        
        # 格式化内容
        paragraphs = c_content.split('\n')
        formatted_content = f'<h1>{c_title}</h1>'
        for para in paragraphs:
            if para.strip():
                formatted_content += f'<p>{para.strip()}</p>'
        
        c.content = formatted_content
        book.add_item(c)
        chapter_objs.append(c)

    # 设置目录和浏览顺序
    book.toc = tuple(chapter_objs)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapter_objs

    # 保存电子书
    epub.write_epub(epub_path, book, {})
    print(f"✅ 成功生成: {epub_path}")

# 使用示例
if __name__ == "__main__":
    txt_to_epub(
        '修罗武神.txt', #txt文件路径
        '修罗武神.epub', #输出epub文件路径
        title="修罗武神", #书名
        author="善良的蜜蜂", #作者
        cover_image="cover.jpg"  # 封面图片路径
    )