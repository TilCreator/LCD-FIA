import argparse
import json
import math
import os

from fia_control import FIA, FIAError
from PIL import Image, ImageOps, ImageDraw

from local_settings import *


class ScrollBuffer:    
    def __init__(self, fia, side, disp_x, disp_y, disp_w, disp_h, int_w, int_h, sc_off_x = 0, sc_off_y = 0, sc_sp_x = 0, sc_sp_y = 0, sc_st_x = 0, sc_st_y = 0):
        self.fia = fia
        self.side = side
        self.disp_x = disp_x
        self.disp_y = disp_y
        self.disp_w = disp_w
        self.disp_h = disp_h
        self.int_w = int_w
        self.int_h = int_h
        self.sc_off_x = sc_off_x or 0
        self.sc_off_y = sc_off_y or 0
        self.sc_sp_x = sc_sp_x or 0
        self.sc_sp_y = sc_sp_y or 0
        self.sc_st_x = sc_st_x or 0
        self.sc_st_y = sc_st_y or 0
        self.id = None
    
    def update(self):
        if self.id is None:
            raise FIAError("Can't update unallocated scroll buffer")
        return self.fia.update_scroll_buffer(self.id, self.side, self.disp_x, self.disp_y, self.disp_w, self.disp_h, self.sc_off_x, self.sc_off_y, self.sc_sp_x, self.sc_sp_y, self.sc_st_x, self.sc_st_y)
    
    def create(self):
        self.id = self.fia.create_scroll_buffer(self.side, self.disp_x, self.disp_y, self.disp_w, self.disp_h, self.int_w, self.int_h, self.sc_off_x, self.sc_off_y, self.sc_sp_x, self.sc_sp_y, self.sc_st_x, self.sc_st_y)
    
    def delete(self):
        if self.id is None:
            raise FIAError("Can't delete unallocated scroll buffer")
        return self.fia.delete_scroll_buffer(self.id)
    
    def send_img(self, img):
        if self.id is None:
            raise FIAError("Can't send image to unallocated scroll buffer")
        
        w, h = img.size
        if w != self.int_w or h != self.int_h:
            raise FIAError("Scroll buffer image doesn't match allocated dimensions")
        
        dest_buf = self.fia.get_destination_buffer()
        try:
            self.fia.set_destination_buffer(self.id)
            self.fia.send_image(img, auto_fit=False)
        finally:
            # Restore old destination buffer
            self.fia.set_destination_buffer(dest_buf)


class LayoutRenderer:
    MAX_FIELD_WIDTH = 10000
    CHAR_MAP = {
        
    }
    
    SIDE_LUT = {
        'a': FIA.SIDE_A,
        'b': FIA.SIDE_B,
        'both': FIA.SIDE_BOTH
    }
    
    def __init__(self, font_dir, fia = None):
        self.font_dir = font_dir
        self.fia = fia
        self.img_mode = 'L'
        self.img_bg = 255
        self.img_fg = 0
        self.scroll_buffers = []
    
    def get_char_filename(self, font, size, code):
        return os.path.join(self.font_dir, font, "size_{}".format(size), "{:x}.bmp".format(code))
    
    def render_character(self, img, x, y, force_width, filename):
        try:
            char_img = Image.open(filename)
        except FileNotFoundError:
            return (False, x, y)
        char_width, char_height = char_img.size
        if force_width is not None:
            if force_width < char_width:
                char_img = char_img.crop((0, 0, force_width, char_height))
            img.paste(char_img, (x, y))
            return (True, x+force_width, y)
        else:
            img.paste(char_img, (x, y))
            return (True, x+char_width, y)

    def render_text(self, width, height, pad_left, pad_top, font, size, align, inverted, spacing, char_width, text):
        text_img = Image.new(self.img_mode, (width, height), color=self.img_bg)
        x = pad_left
        y = pad_top
        for char in text:
            if char in self.CHAR_MAP:
                code = self.CHAR_MAP[char]
            else:
                code = ord(char)
            success, x, y = self.render_character(text_img, x, y, char_width, self.get_char_filename(font, size, code))
            x += spacing
        if align in ('center', 'right'):
            bbox = ImageOps.invert(text_img).getbbox()
            if bbox is not None:
                cropped = text_img.crop((bbox[0], 0, bbox[2], height-1))
                cropped_width = cropped.size[0]
                text_img = Image.new(self.img_mode, (width, height), color=self.img_bg)
                if align == 'center':
                    x_offset = (width - cropped_width) // 2
                elif align == 'right':
                    x_offset = width - cropped_width
                text_img.paste(cropped, (x_offset, 0))
        if inverted:
            text_img = ImageOps.invert(text_img)
        return text_img

    def render_image(self, width, height, pad_left, pad_top, inverted, value_img):
        new_img = Image.new(self.img_mode, (width, height), color=self.img_bg)
        new_img.paste(value_img, (pad_left, pad_top))
        if inverted:
            new_img = ImageOps.invert(new_img)
        return new_img

    def render_placeholder(self, img, side, placeholder, value, render_boxes, render_content):
        x = placeholder.get('x')
        y = placeholder.get('y')
        width = placeholder.get('width')
        height = placeholder.get('height')
        pad_left = placeholder.get('pad_left')
        pad_top = placeholder.get('pad_top')
        p_type = placeholder.get('type')
        inverted = placeholder.get('inverted')
        default = placeholder.get('default')
        
        if render_content and p_type == 'text':
            if not value:
                return
            font = placeholder.get('font')
            size = placeholder.get('size')
            align = placeholder.get('align')
            spacing = placeholder.get('spacing', 0)
            char_width = placeholder.get('char_width', None)
            
            scroll = placeholder.get('scroll', False)
            only_scroll_if_wider = placeholder.get('only_scroll_if_wider', False)
            if scroll:
                int_w = placeholder.get('internal_width')
                int_h = placeholder.get('internal_height', math.ceil(height / 8) * 8)
                sc_off_x = placeholder.get('scroll_offset_x')
                sc_off_y = placeholder.get('scroll_offset_y')
                sc_sp_x = placeholder.get('scroll_speed_x', 5)
                sc_sp_y = placeholder.get('scroll_speed_y', 0)
                sc_st_x = placeholder.get('scroll_step_x', 1)
                sc_st_y = placeholder.get('scroll_step_y', 1)
                post_clearance = placeholder.get('post_clearance', 0)
                # "not inverted" because usually the whole thing
                # is inverted until the end
                # but in case of scroll buffers we pass the image early
                # so we have to invert the inverting
                if int_w is None:
                    # No internal width specified, use auto-crop
                    txt = self.render_text(self.MAX_FIELD_WIDTH, height, pad_left, pad_top, font, size, align, not inverted, spacing, char_width, value)
                    if inverted:
                        tmp = ImageOps.invert(txt)
                        bbox = tmp.getbbox()
                        required_width = bbox[2]
                        if only_scroll_if_wider and required_width <= width:
                            scroll = False
                        else:
                            int_w = max(required_width + post_clearance, width)
                            txt = txt.crop((0, 0, int_w, height))
                else:
                    txt = self.render_text(int_w, height, pad_left, pad_top, font, size, align, not inverted, spacing, char_width, value)
                if scroll:
                    scroll_buffer = ScrollBuffer(self.fia, side, x, y, width, height, int_w, int_h, sc_off_x, sc_off_y, sc_sp_x, sc_sp_y, sc_st_x, sc_st_y)
                    scroll_buffer.create()
                    print("Allocated scroll buffer {}".format(scroll_buffer.id))
                    scroll_buffer.send_img(txt)
                    self.scroll_buffers.append(scroll_buffer)
            if not scroll:
                txt = self.render_text(width, height, pad_left, pad_top, font, size, align, inverted, spacing, char_width, value)
                img.paste(txt, (x, y))
        elif render_content and p_type == 'image':
            if not value:
                return
            try:
                value_img = Image.open(value)
            except FileNotFoundError:
                return
            img.paste(self.render_image(width, height, pad_left, pad_top, inverted, value_img), (x, y))
        elif p_type == 'line':
            x2 = placeholder.get('x2', 0)
            y2 = placeholder.get('y2', 0)
            line_width = placeholder.get('line_width', 1)
            draw = ImageDraw.Draw(img)
            color = self.img_bg if inverted else self.img_fg
            draw.line((x, y, x2, y2), fill=color, width=line_width)
        elif p_type == 'rectangle':
            fill = placeholder.get('fill')
            draw = ImageDraw.Draw(img)
            color = self.img_bg if inverted else self.img_fg
            draw.rectangle((x, y, x+width-1, y+height-1), outline=color, fill=color if fill else None)
        
        if render_boxes:
            draw = ImageDraw.Draw(img)
            draw.rectangle((x, y, x+width-1, y+height-1), outline=self.img_fg)
    
    def render(self, layout, data, render_boxes = False, render_content = True):
        img = Image.new(self.img_mode, (layout['width'], layout['height']), color=self.img_bg)
        side = self.SIDE_LUT.get(layout.get('side', 'both'), self.SIDE_LUT['both'])
        if render_content:
            for placeholder in layout['placeholders']:
                value = data['placeholders'].get(placeholder['name'], placeholder.get('default'))
                self.render_placeholder(img, side, placeholder, value, render_boxes=False, render_content=True)
        if render_boxes:
            for placeholder in layout['placeholders']:
                self.render_placeholder(img, side, placeholder, value=None, render_boxes=True, render_content=False)
        return ImageOps.invert(img)
    
    def display(self, *args, **kwargs):
        if self.fia is None:
            raise ValueError("Can't display image without fia argument")
        img = self.render(*args, **kwargs)
        self.fia.send_image(img)
    
    def free_scroll_buffers(self):
        for buf in self.scroll_buffers:
            buf.delete()
        self.scroll_buffers = []


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', '-o', required=False, type=str)
    parser.add_argument('--layout', '-l', required=True, type=str)
    parser.add_argument('--font-dir', '-fd', required=True, type=str)
    parser.add_argument('--width', '-w', required=True, type=int)
    parser.add_argument('--height', '-h', required=True, type=int)
    parser.add_argument('--data', '-d', action='append', nargs=2, metavar=("key", "value"))
    args = parser.parse_args()
    
    renderer = LayoutRenderer(args.font_dir)
    
    with open(args.layout, 'r', encoding='utf-8') as f:
        layout = json.load(f)
    
    data = {
        'placeholders': dict(args.data) if args.data is not None else {}
    }
    
    img = renderer.render(layout, data)
    
    if args.output:
        img.save(args.output)
    else:
        fia = FIA("/dev/ttyAMA1", (3, 0), width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
        fia.send_image(img)


if __name__ == "__main__":
    main()
