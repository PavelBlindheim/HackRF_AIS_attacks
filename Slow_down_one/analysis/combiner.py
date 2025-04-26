from PIL import Image
import os

def merge_images(folder1, folder2, output_folder, overlap=50):
    os.makedirs(output_folder, exist_ok=True)
    
    image_names = ["0ms", "100ms", "150ms", "200ms", "250ms"]
    
    for name in image_names:
        path1 = os.path.join(folder1, f"{name}.png")
        path2 = os.path.join(folder2, f"{name}.png")
        
        if not os.path.exists(path1) or not os.path.exists(path2):
            print(f"Skipping {name}.png, one of the images is missing.")
            continue
        
        img1 = Image.open(path1)
        img2 = Image.open(path2)
        
        width1, height1 = img1.size
        width2, height2 = img2.size
        
        new_width = width1 + width2 - overlap
        new_height = max(height1, height2)
        
        merged_img = Image.new("RGB", (new_width, new_height))
        merged_img.paste(img1, (0, 0))
        merged_img.paste(img2, (width1 - overlap, 0))
        
        output_path = os.path.join(output_folder, f"merged_{name}.png")
        merged_img.save(output_path)
        print(f"Saved: {output_path}")

# Example usage
merge_images("delay_variance_pictures", "successrates_pictures", "merged_pictures")
