"""Convert PNG to ICO format for Windows icon."""
from pathlib import Path
try:
    from PIL import Image
    
    def convert_png_to_ico():
        """Convert avatar.png to avatar.ico."""
        src_dir = Path(__file__).parent / "src"
        png_path = src_dir / "images" / "avatar.png"
        ico_path = src_dir / "images" / "avatar.ico"
        
        if not png_path.exists():
            print(f"Error: {png_path} not found!")
            return False
        
        try:
            # Open PNG image
            img = Image.open(png_path)
            
            # Create ICO with multiple sizes (Windows standard)
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Save as ICO
            img.save(ico_path, format='ICO', sizes=sizes)
            print(f"Successfully converted {png_path.name} to {ico_path.name}")
            print(f"ICO file saved at: {ico_path}")
            return True
        except Exception as e:
            print(f"Error converting image: {e}")
            return False
    
    if __name__ == "__main__":
        convert_png_to_ico()
        
except ImportError:
    print("PIL/Pillow not installed. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    print("Please run this script again.")

