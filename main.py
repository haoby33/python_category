import os
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 定义文件类型分类
FILE_CATEGORIES = {
    "文档": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "视频": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm", ".m4v"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "压缩文件": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "程序": [".exe", ".msi", ".bat", ".sh", ".apk", ".deb", ".rpm"],
    "代码": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".php", ".rb"],
    "字体": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "电子书": [".epub", ".mobi", ".azw3"],
    "其他": []  # 未分类文件
}


class DownloadOrganizer(FileSystemEventHandler):
    def __init__(self, download_path):
        self.download_path = download_path
        self.ensure_category_folders()

    def ensure_category_folders(self):
        """确保所有分类文件夹存在"""
        for category in FILE_CATEGORIES.keys():
            category_path = os.path.join(self.download_path, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)

    def get_file_category(self, file_extension):
        """根据文件扩展名获取文件分类"""
        for category, extensions in FILE_CATEGORIES.items():
            if file_extension.lower() in extensions:
                return category
        return "其他"

    def organize_file(self, file_path):
        """整理单个文件"""
        if os.path.isdir(file_path):
            return  # 跳过目录

        filename = os.path.basename(file_path)
        # 跳过临时文件
        if filename.startswith('~') or filename.startswith('.'):
            return

        file_extension = os.path.splitext(filename)[1]
        category = self.get_file_category(file_extension)

        # 目标路径
        dest_folder = os.path.join(self.download_path, category)
        dest_path = os.path.join(dest_folder, filename)

        # 处理文件名冲突
        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{counter}{ext}"
            dest_path = os.path.join(dest_folder, new_filename)
            counter += 1

        try:
            shutil.move(file_path, dest_path)
            print(f"已移动: {filename} -> {category}")
        except Exception as e:
            print(f"移动文件失败 {filename}: {str(e)}")

    def organize_all_files(self):
        """整理下载目录中的所有文件"""
        for filename in os.listdir(self.download_path):
            file_path = os.path.join(self.download_path, filename)
            if os.path.isfile(file_path):
                self.organize_file(file_path)

    def on_created(self, event):
        """监控文件创建事件"""
        if not event.is_directory:
            # 等待文件完全写入
            time.sleep(1)
            self.organize_file(event.src_path)


def main():
    download_path = r"C:\Users\krian\Downloads"

    if not os.path.exists(download_path):
        print(f"错误: 下载目录不存在 {download_path}")
        return

    print(f"开始整理下载目录: {download_path}")

    # 创建整理器实例
    organizer = DownloadOrganizer(download_path)

    # 先整理已存在的文件
    organizer.organize_all_files()

    # 设置监控（可选）
    use_watchdog = input("是否启用实时监控? (y/n): ").lower().startswith('y')

    if use_watchdog:
        print("启用实时监控中... 按 Ctrl+C 停止")
        event_handler = organizer
        observer = Observer()
        observer.schedule(event_handler, download_path, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        print("文件整理完成!")


if __name__ == "__main__":
    main()