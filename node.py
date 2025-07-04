import numpy as np
import torch
from PIL import Image, ImageDraw

MANIFEST = {
    "name": "ComfyUI Easy Padding",
    "version": (1, 0, 3),
    "author": "ealkanat",
    "project": "https://github.com/erkana/comfyui_easy_padding",
    "description": "A simple custom node for creates padding for given image",
}


class AddPadding:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "left": ("INT", {"default": 0, "step": 1, "min": 0, "max": 4096}),
                "top": ("INT", {"default": 0, "step": 1, "min": 0, "max": 4096}),
                "right": ("INT", {"default": 0, "step": 1, "min": 0, "max": 4096}),
                "bottom": ("INT", {"default": 0, "step": 1, "min": 0, "max": 4096}),
                "color": ("STRING", {"default": "#ffffff"}),
                "transparent": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "optional_mask_in": ("MASK", {"default": None}),
            },
        }

    CATEGORY = "ComfyUI Easy Padding"
    DESCRIPTION = "A simple custom node for creating padding for given image"

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "pad"

    def pad(self, image, left, top, right, bottom, color, transparent, optional_mask_in=None):
        padded_images = []
        masks = []
        image = [self.tensor2pil(img) for img in image]
        optional_mask_in = [self.tensor2pil(mask) for mask in optional_mask_in] if optional_mask_in is not None else [None] * len(image)
        for img, mask_in in zip(image, optional_mask_in):
            padded_image = Image.new(
                "RGBA" if transparent else "RGB",
                (img.width + left + right, img.height + top + bottom),
                (0, 0, 0, 0) if transparent else self.hex_to_tuple(color)
            )
            padded_image.paste(img, (left, top))
            padded_images.append(self.pil2tensor(padded_image))

            mask_image = Image.new("L", (img.width + left + right, img.height + top + bottom), 255)
            if mask_in is not None:
                mask_image.paste(mask_in, (left, top))
            else:
                shape = (left, top, img.width + left - 1, img.height + top - 1)
                draw = ImageDraw.Draw(mask_image)
                draw.rectangle(shape, fill=0)
            masks.append(self.pil2tensor(mask_image))

        return (torch.cat(padded_images, dim=0), torch.cat(masks, dim=0))

    def hex_to_tuple(self, color: str):
        if not isinstance(color, str):
            raise ValueError("Color must be a hex string")
        color = color.strip("#")
        if len(color) not in (3, 6):
            raise ValueError("Color must be a valid hex string of length 3 or 6 (e.g., '#fff' or '#ffffff')")
        if len(color) == 3:
            color = ''.join([c*2 for c in color])
        return tuple(int(color[i:i + 2], 16) for i in range(0, 6, 2))

    # Tensor to PIL
    def tensor2pil(self, image):
        return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

    # PIL to Tensor
    def pil2tensor(self, image):
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


NODE_CLASS_MAPPINGS = {
    "comfyui-easy-padding": AddPadding,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "comfyui-easy-padding": "ComfyUI Easy Padding",
}