import moderngl as _mgl
import glm as _glm
import time as _time
import numpy as _np
import pathlib as _path
import string as _string
import pygame
import sys
import os
import random
import math
import typing as typing
# todo: particles, collision
# todo: finish animation, button logic


class PGLError(RuntimeError): ...


Rect = pygame.FRect
Vec = pygame.Vector2
STATIC = "static"
UPDATE = "update"
INVISIBLE = "invisible"
INVISIBLE_COLOR = (0, 0, 0, 0)
KEYBOARD = "key"
MOUSE = "mouse"
PRESS = "press"
RELEASE = "release"
UNLIT_SHADER = "unlit"
LIT_SHADER = "lit"
UI_SHADER = "ui"
REPLACE_SHADER = "replace"
TOPDOWN_SORT = "topdown"
TEXTPOS_CENTER = "center"
TEXTPOS_TL = "tl"
TEXTPOS_BL = "bl"
TEXTPOS_TR = "tr"
TEXTPOS_BR = "br"
TEXTPOS_MIDL = "ml"
TEXTPOS_MIDR = "ml"
TEXTPOS_MIDT = "ml"
TEXTPOS_MIDB = "ml"
ALIGN_CENTER = "center"
ALIGN_LEFT = "left"
ALIGN_RIGHT = "right"
NOISE_LT = "lt"
NOISE_GT = "gt"
NOISE_SIMPLEX_2D = "simplex2D"
NOISE_SIMPLEX_3D = "simplex3D"
NOISE_PERLIN_1D = "perlin1D"
NOISE_PERLIN_2D = "perlin2D"
NOISE_PERLIN_3D = "perlin3D"
ANIMTYPE_NUMBER = "number"
ANIMTYPE_COLOR = "color"
ANIMTYPE_SEQUENCE = "sequence"


class _internal:
    _tag_entities = {}
    _update_entities = []
    _scenes = {}
    _scene = None
    _clock = pygame.Clock()
    _win = None
    _gl_context = None
    _shaders = {}
    _proj_mat4 = None
    _view_mat4 = None
    _unit = 1
    _scene_init_complete = True
    _binds = {}
    _max_lights = 100
    _samplers_amount = 1
    _ambient_light = "0.15, 0.15, 0.15, 1"
    _layer_groups = {}
    _cont_entities = {}
    _timers = []
    _custom_image_loaders = []
    _light_filter = None
    _lights = []
    _fonts_data = {}
    _noise = None
    _sounds = {}
    _musics = {}
    _music_playing = None
    _sound_volume = 1
    _music_volume = 1
    _atlas = {
        "ID": 0,
        "surfaces": {},
        "texture": None,
        "height": 0,
        "width": 0,
        "uvs": {},
    }
    _font_atlas = {
        "ID": 1,
        "surfaces": {},
        "texture": None,
        "height": 0,
        "width": 0,
        "uvs": {},
    }
    _animations = []
    _SHADER_SOURCE = {
        "replace": {
            "vert": """
#version 450 core

layout (location = 0) in vec2 vPos;
layout (location = 1) in vec4 vCol;
layout (location = 2) in vec2 vUV;
layout (location = 3) in float vTexID;

uniform mat4 proj;
uniform mat4 view;

out vec4 fCol;
out vec2 fUV;
out float fTexID;

void main() {
    gl_Position = proj*view*vec4(vec3(vPos, 0), 1.0);
    fCol = vCol;
    fUV = vUV;
    fTexID = vTexID;
}
""",
            "frag": """
#version 450 core

in vec4 fCol;
in vec2 fUV;
in float fTexID;
out vec4 oCol;

uniform sampler2D textures[{SAMPLERS_AMOUNT}];

void main() {
    vec4 texCol = texture2D(textures[int(fTexID)], fUV);
    if (texCol.a <= 0) {
        discard;
    }
    oCol = vec4(fCol.xyz * ((texCol.r+texCol.g+texCol.b)/3.0), fCol.a*texCol.a);
}""",
        },
        "ui": {
            "vert": """
#version 450 core

layout (location = 0) in vec2 vPos;
layout (location = 1) in vec4 vCol;
layout (location = 2) in vec2 vUV;
layout (location = 3) in float vTexID;

uniform mat4 proj;

out vec4 fCol;
out vec2 fUV;
flat out float fTexID;

void main() {
    gl_Position = proj * vec4(vPos, 0.0, 1.0);
    fCol = vCol;
    fUV = vUV;
    fTexID = vTexID;
}""",
            "frag": """
#version 450 core

in vec4 fCol;
in vec2 fUV;
in float fTexID;

out vec4 oCol;

uniform sampler2D textures[{SAMPLERS_AMOUNT}];

void main() {
    oCol = texture(textures[int(fTexID)], fUV) * fCol;
    if (oCol.a <= 0.0) {
        discard;
    }
}""",
        },
        "lit": {
            "vert": """
#version 450 core

layout (location = 0) in vec2 vPos;
layout (location = 1) in vec4 vCol;
layout (location = 2) in vec2 vUV;
layout (location = 3) in float vTexID;

out vec2 fPos;
out vec4 fCol;
out vec2 fUV;
flat out float fTexID;

uniform mat4 proj;
uniform mat4 view;

void main() {
    gl_Position = proj * view * vec4(vPos, 0.0, 1.0);
    fPos = vPos;
    fCol = vCol;
    fUV = vUV;
    fTexID = vTexID;
}""",
            "frag": """
#version 450 core

in vec2 fPos;
in vec4 fCol;
in vec2 fUV;
in float fTexID;

out vec4 oCol;

uniform float numLights;
uniform sampler2D textures[{SAMPLERS_AMOUNT}];
uniform float lightData[{MAX_LIGHTS}*7];

const vec4 BASE_LIGHT = vec4({AMBIENT_LIGHT});

void main() {
    vec4 originalCol = texture(textures[int(fTexID)], fUV) * fCol;
    if (originalCol.a <= 0.01) {
        discard;
    }
    vec4 finalCol = originalCol * BASE_LIGHT;
    
    for (int i = 0; i < int(numLights)*7; i+=7) {
        vec2 direction = fPos - vec2(lightData[i], lightData[i+1]);
        float distanceSq = dot(direction, direction);
        float rangeSq = lightData[i+5] * lightData[i+5];
        float attenuation = max(1.0 - distanceSq / rangeSq, 0.0);
        finalCol += vec4(lightData[i+2], lightData[i+3], lightData[i+4], 1.0) *
                    originalCol *
                    attenuation *
                    lightData[i+6];
    }
    oCol = finalCol;
}""",
        },
        "unlit": {
            "vert": """
#version 450 core

layout (location = 0) in vec2 vPos;
layout (location = 1) in vec4 vCol;
layout (location = 2) in vec2 vUV;
layout (location = 3) in float vTexID;

uniform mat4 proj;
uniform mat4 view;

out vec4 fCol;
out vec2 fUV;
flat out float fTexID;

void main() {
    gl_Position = proj * view * vec4(vPos, 0.0, 1.0);
    fCol = vCol;
    fUV = vUV;
    fTexID = vTexID;
}
        """,
            "frag": """
#version 450 core

in vec4 fCol;
in vec2 fUV;
in float fTexID;

out vec4 oCol;

uniform sampler2D textures[{SAMPLERS_AMOUNT}];

void main() {
    oCol = texture(textures[int(fTexID)], fUV) * fCol;
    if (oCol.a <= 0.0) {
        discard;
    }
}
        """,
        },
    }

    def _init(config):
        pygame.init()

        size = pygame.display.get_desktop_sizes()[0]
        resizable = True
        borderless = False
        if "window" in config:
            if "resizable" in config["window"]:
                if config["window"]["resizable"]:
                    resizable = config["window"]["resizable"]
            if "borderless" in config["window"] and config["window"]["borderless"]:
                borderless = True
            if "size" in config["window"] and config["window"]["size"] != "maximized":
                size = config["window"]["size"]
        _internal._win = pygame.Window(
            "PGL Window", size, opengl=True, resizable=resizable, borderless=borderless
        )
        if "window" in config and "title" in config["window"]:
            _internal._win.title = config["window"]["title"]

        _internal._gl_context = _mgl.create_context()
        _internal._gl_context.enable(_mgl.BLEND)
        _internal._gl_context.blend_func = (
            _internal._gl_context.SRC_ALPHA,
            _internal._gl_context.ONE_MINUS_SRC_ALPHA,
        )

        if "binds" in config:
            for name, data in config["binds"].items():
                if isinstance(data, list):
                    alts = []
                    main_bind = _internal._parse_bind(data)
                else:
                    if "main" not in data:
                        raise PGLError(f"Bind {name} must specify a main bind code")
                    main_bind = _internal._parse_bind(data["main"])
                    alts = []
                    if "alts" in data:
                        for alt in data["alts"]:
                            alts.append(_internal._parse_bind(alt))
                _internal._binds[name] = _internal._Bind(main_bind, *alts)

        if "game" in config:
            if (
                "framerate-limit" in config["game"]
                and config["game"]["framerate-limit"] != "unlimited"
            ):
                Time.fps_limit = max(0, config["game"]["framerate-limit"])
            if "max-lights" in config["game"]:
                if not isinstance(config["game"]["max-lights"], int):
                    raise PGLError("Max lights value must be an integer")
                _internal._max_lights = max(0, config["game"]["max-lights"])
                if _internal._max_lights > 145:
                    raise PGLError("Max lights value must be <= 145")
            if "ambient-light" in config["game"]:
                _internal._ambient_light = config["game"]["ambient-light"]

        _internal._load_images(config["project-path"])
        if "fonts" in config:
            _internal._load_fonts(config["fonts"], config["project-path"])
        if "sounds" in config:
            _internal._load_sounds(config["sounds"], config["project-path"])

        for name, data in _internal._SHADER_SOURCE.items():
            fragment_data = data["frag"].replace(
                "{SAMPLERS_AMOUNT}", f"{_internal._samplers_amount}"
            )
            fragment_data = fragment_data.replace(
                "{MAX_LIGHTS}", f"{_internal._max_lights}"
            )
            fragment_data = fragment_data.replace(
                "{AMBIENT_LIGHT}", ", ".join(list(map(str, _internal._ambient_light)))
            )
            _internal._shaders[name] = _internal._gl_context.program(
                vertex_shader=data["vert"], fragment_shader=fragment_data
            )

        _internal._LayerGroup._apply_make_buffers()
        _internal._update_proj()
        _internal._update_main()

        if "game" in config and "start-scene" in config["game"]:
            Scene.load(config["game"]["start-scene"])
        else:
            raise PGLError("game:start-scene entry missing in config.json")
        _internal._scene.on_window_resize()

    def _load_sounds(sounds, project_path):
        if not isinstance(sounds, dict):
            raise PGLError("Sounds entry of config.json must be a dictionary")
        for name, data in sounds.items():
            if not isinstance(data, dict):
                raise PGLError("Sound entry of config.json:sounds must be a dictionary")
            volume, ext, music = 1, "ogg", False
            if "volume" in data:
                volume = data["volume"]
            if "ext" in data:
                ext = data["ext"]
            if "music" in data:
                music = data["music"]
            if music and ext == "folder":
                raise PGLError("Sound with ext folder can't be music")
            sounds = []
            for dirpath, subfolders, files in os.walk(f"{project_path}assets/"):
                found = False
                if ext == "folder":
                    for folder in subfolders:
                        if folder == name:
                            for fileinfolder in os.listdir(f"{dirpath}/{folder}"):
                                sounds.append(f"{dirpath}/{folder}/{fileinfolder}")
                            found = True
                            break
                else:
                    for filename in files:
                        if filename == f"{name}.{ext}":
                            sounds.append(f"{dirpath}/{filename}")
                            found = True
                            break
                if found:
                    break
            if len(sounds) == 0:
                if ext == "folder":
                    raise PGLError(
                        f"Sound folder {name} was not found. Did you assign the wrong extension?"
                    )
                raise PGLError(
                    f"Sound {name}.{ext} was not found. Did you forget to assign the correct extension?"
                )
            if music:
                _internal._musics[name] = {"path": sounds[0], "volume": volume}
            else:
                _internal._sounds[name] = _internal._SoundAsset(sounds, volume)

    def _parse_bind(data):
        if isinstance(data, _internal._BindCode):
            ret = [data.code]
            if data.type == MOUSE:
                ret.append(MOUSE)
            if data.direction == RELEASE:
                ret.append(RELEASE)
            return ret
        if not isinstance(data, list):
            raise PGLError(
                "Bind code data must be a list with the code as the first element and optional MOUSE and RELEASE flags as the other elements"
            )
        code, type_, dir_ = data[0], KEYBOARD, PRESS
        if isinstance(code, str):
            code = getattr(pygame, code)
        if MOUSE in data:
            type_ = MOUSE
        if RELEASE in data:
            dir_ = RELEASE
        return _internal._BindCode(type_, code, dir_)

    def _load_fonts(fonts_data, project_path):
        surfaces = _internal._font_atlas["surfaces"]
        if not isinstance(fonts_data, dict):
            raise PGLError("Fonts entry of config.json must be a dictionary")
        for name, udata in fonts_data.items():
            if not isinstance(udata, dict):
                raise PGLError("Font entry of config.json:fonts must be a dictionary")
            font_func = pygame.Font
            font_path = None
            bitmap_size = 100
            if "bitmap-size" in udata:
                bitmap_size = udata["bitmap-size"]
            if "path" in udata:
                real_path = _path.Path(f"{project_path}assets/{udata['path']}")
                if real_path.exists():
                    font_path = real_path
                else:
                    font_path = udata["path"]
                    font_func = pygame.font.SysFont
            pg_font = font_func(font_path, bitmap_size)
            antialas = True
            base_scale = 1
            if "bold" in udata and udata["bold"]:
                pg_font.bold = True
            if "italic" in udata and udata["italic"]:
                pg_font.italic = True
            if "strikethrough" in udata and udata["strikethrough"]:
                pg_font.strikethrough = True
            if "underline" in udata and udata["underline"]:
                pg_font.underline = True
            if "antialias" in udata and not udata["antialias"]:
                antialas = False
            if "chars" in udata:
                chars = udata["chars"]
            else:
                chars = (
                    _string.ascii_letters + _string.digits + _string.punctuation + " "
                )
            if "extra-chars" in udata:
                chars += udata["extra-chars"]
            if "base-scale" in udata:
                base_scale = udata["base-scale"]
            data = {
                "height": pg_font.get_height() / bitmap_size * base_scale,
                "chars_w": {},
            }
            for char in chars:
                surfaces[f"{name}_{char}"] = pg_font.render(char, antialas, "white")
                data["chars_w"][char] = pg_font.size(char)[0] / bitmap_size * base_scale
            _internal._fonts_data[name] = data
        if len(surfaces) <= 0:
            return
        _internal._samplers_amount += 1
        _internal._build_atlas(_internal._font_atlas)

    def _load_images(project_path):
        square = pygame.Surface((10, 10))
        square.fill("white")
        surfaces = _internal._atlas["surfaces"]
        surfaces["square"] = square

        for dirpath, _, files in os.walk(f"{project_path}assets"):
            for file in files:
                file = _path.Path(dirpath + "/" + file)
                if not file.stem.startswith("ignore"):
                    try:
                        surf = pygame.image.load(str(file)).convert_alpha()
                        surfaces[file.stem] = surf
                    except Exception:
                        pass
        for func in _internal._custom_image_loaders:
            surfaces.update(func())
        _internal._build_atlas(_internal._atlas)

    def _build_atlas(data):
        surfs = sorted(
            list(data["surfaces"].values()),
            key=lambda surf: surf.get_height(),
            reverse=True,
        )
        inv_surfs = {id(surf): name for name, surf in data["surfaces"].items()}
        data["height"] = math.sqrt(
            sum([surf.get_width() * surf.get_height() for surf in surfs])
        )
        positions = []
        x = y = bw = 0
        for surf in surfs:
            w, h = surf.get_size()
            if data["height"] - y < h:
                y = 0
                x += bw + 2
                bw = 0
            if w > bw:
                bw = w
            positions.append([surf, w, h, x, y])
            y += h + 2
        data["width"] = x + bw
        main_surf = pygame.Surface(
            (data["width"], int(data["height"] * 1.01)), pygame.SRCALPHA
        )
        main_surf.fill(0)
        for surf, w, h, x, y in positions:
            surf: pygame.Surface
            data["uvs"][inv_surfs[id(surf)]] = _internal._RenderGroup._uvs_atlas(
                data["width"], int(data["height"] * 1.01), w, h, x, y
            )
            a = surf.get_at((0, 0)).a
            b = surf.get_at((w - 1, h - 1)).a
            c = surf.get_at((0, h - 1)).a
            d = surf.get_at((w - 1, 0)).a
            if a >= 255 and b >= 255 and c >= 255 and d >= 255:
                main_surf.blit(
                    pygame.transform.scale(surf, (w + 2, h + 2)), (x - 1, y - 1)
                )
            main_surf.blit(surf, (x, y))
        if False:
            pygame.image.save(
                main_surf, "test.png" if data["ID"] == 0 else "fonttest.png"
            )
        data["texture"] = _internal._gl_context.texture(
            main_surf.get_size(), 4, pygame.image.tobytes(main_surf, "RGBA", False)
        )
        data["texture"].filter = (_mgl.NEAREST, _mgl.NEAREST)

    def _main(config):
        _internal._init(config)
        Frame.valid = True

        while True:
            _internal._update_main()
            if len(_internal._scene.clear_color) != 4:
                raise PGLError("Scene clear color must have 4 components")
            _internal._gl_context.clear(*_internal._scene.clear_color)

            for event in Frame.events:
                if event.type == pygame.QUIT and _internal._scene.can_quit():
                    _internal._scene.on_quit()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    _internal._update_proj()
                    _internal._update_view()
                    _internal._scene.on_window_resize()
                elif event.type == pygame.MOUSEWHEEL:
                    Frame.mouse_wheel.x += event.x
                    Frame.mouse_wheel.y += event.y

            for timer in _internal._timers:
                if (
                    timer.start_time != -1
                    and Time.time - timer.start_time >= timer.cooldown
                ):
                    timer.start_time = -1
                    can_restart = timer.end_callback(
                        *timer.callback_args, **timer.callback_kwargs
                    )
                    if can_restart:
                        timer.start()

            for anim in _internal._animations:
                anim.update_value()

            _internal._scene.update()
            for e in _internal._update_entities:
                e.update()
            _internal._LayerGroup._sorted_update_render()

            _internal._win.flip()
            if Time.scale < 0:
                raise PGLError("Time scale must be positive")
            Time.delta = (
                _internal._clock.tick_busy_loop(Time.fps_limit) / 1000
            ) * Time.scale
            Time.time += Time.delta

    def _update_main():
        Frame.events = pygame.event.get()
        Frame.screen_mouse = Vec(pygame.mouse.get_pos())
        Frame.mouse_rel = Vec(pygame.mouse.get_rel())
        Frame.keys = pygame.key.get_pressed()
        Frame.buttons = pygame.mouse.get_pressed()
        Frame.keys_just_pressed = pygame.key.get_just_pressed()
        Frame.keys_just_released = pygame.key.get_just_released()
        Frame.buttons_just_pressed = pygame.mouse.get_just_pressed()
        Frame.buttons_just_released = pygame.mouse.get_just_released()
        Frame.absolute_time = pygame.time.get_ticks() / 1000
        Frame.mouse_wheel = Vec()

        if Camera.zoom <= 0:
            raise PGLError("Camera zoom must be greater than zero")

        _internal._update_view()
        _internal._upload_samplers()
        _internal._update_light()

    def _update_proj():
        win_size = Window.size

        ratio = win_size.x / win_size.y
        inv_ratio = win_size.y / win_size.x

        if ratio > inv_ratio:
            _internal._proj_mat4 = _glm.ortho(
                -10 * ratio, 10 * ratio, 10, -10, Camera.near_plane, Camera.far_plane
            )
            _internal._unit = win_size.y / 10
        else:
            _internal._proj_mat4 = _glm.ortho(
                -10,
                10,
                10 * inv_ratio,
                -10 * inv_ratio,
                Camera.near_plane,
                Camera.far_plane,
            )
            _internal._unit = win_size.x / 10

    def _update_view():
        _internal._view_mat4 = _glm.scale(
            _glm.translate(_glm.vec3(-Camera.position.x, -Camera.position.y, 0)),
            _glm.vec3(Camera.zoom, Camera.zoom, 1),
        )
        size = Window.size

        Window.rect = pygame.FRect(
            -size.x / _internal._unit,
            -size.y / _internal._unit,
            (size.x / _internal._unit) * 2,
            (size.y / _internal._unit) * 2,
        )
        Camera.rect = pygame.FRect(
            Camera.screen_to_world(pygame.Vector2(0, 0)),
            (Window.rect.w / Camera.zoom, Window.rect.h / Camera.zoom),
        )

        Camera.ui_mouse = Camera.screen_to_ui(Frame.screen_mouse)
        Camera.world_mouse = Camera.screen_to_world(Frame.screen_mouse)

        if _internal._proj_mat4 is None or _internal._view_mat4 is None:
            return
        for shader in _internal._shaders.values():
            proj_uniform = shader.get("proj", None)
            view_uniform = shader.get("view", None)
            if proj_uniform is not None:
                proj_uniform.write(_internal._proj_mat4)
            if view_uniform is not None:
                view_uniform.write(_internal._view_mat4)

    def _upload_samplers():
        data = _np.fromiter(list(range(_internal._samplers_amount)), dtype=_np.int32)
        for shader in _internal._shaders.values():
            uniform = shader.get("textures", None)
            if uniform is not None:
                uniform.write(data)

        _internal._atlas["texture"].use(_internal._atlas["ID"])
        if _internal._font_atlas["texture"]:
            _internal._font_atlas["texture"].use(_internal._font_atlas["ID"])

    def _update_light():
        filter_func = _internal._default_light_filter
        if _internal._light_filter:
            filter_func = _internal._light_filter
        light_data = []
        light_num = 0
        for light in filter(filter_func, _internal._lights):
            if not light.visible:
                continue
            light_num += 1
            light_data += [
                *light.rect.center,
                *light.color,
                light.rect.w,
                light.intensity,
            ]
        _internal._shaders["lit"]["numLights"] = min(light_num, _internal._max_lights)
        _internal._shaders["lit"]["lightData"] = _np.fromiter(
            light_data, dtype=_np.float32
        )

    def _default_light_filter(light):
        return light.visible and light.rect.colliderect(Camera.rect)

    class _SoundAsset:
        def __init__(self, paths, volume):
            self._pg_sounds = [pygame.mixer.Sound(path) for path in paths]
            for sound in self._pg_sounds:
                sound.set_volume(volume)
            self._volume = volume

        def _update_volume(self):
            for sound in self._pg_sounds:
                sound.set_volume(self._volume * _internal._sound_volume)

        def _stop(self):
            for sound in self._pg_sounds:
                sound.stop()

        def _play(self, stop, loops, fade):
            if stop:
                for sound in self._pg_sounds:
                    sound.stop()
            if len(self._pg_sounds) > 1:
                self._pg_sounds[0].play(loops, fade_ms=fade)
                return
            random.choice(self._pg_sounds).play(loops, fade_ms=fade)

    class _StaticType:
        def __init__(self, *args, **kwargs):
            raise PGLError(
                f"'{self.__class__.__name__}' is a static class and cannot be instantiated"
            )

    class _WindowType(type):
        @property
        def window(self):
            return _internal._win

        @property
        def title(self):
            return _internal._win.title

        @title.setter
        def title(self, v):
            _internal._win.title = v

        @property
        def size(self):
            return Vec(_internal._win.size)

        @size.setter
        def size(self, v):
            if v == "maximized":
                v = pygame.display.get_desktop_sizes()[0]
            _internal._win.size = v

        @property
        def position(self):
            return Vec(_internal._win.position)

        @position.setter
        def position(self, v):
            if v == "centered":
                mw, mh = pygame.display.get_desktop_sizes()[0]
                v = (
                    int(mw / 2) - _internal._win.size[0],
                    int(mh / 2) - _internal._win.size[1],
                )
            _internal._win.position = v

        @property
        def opacity(self):
            return _internal._win.opacity

        @opacity.setter
        def opactity(self, v):
            _internal._win.opacity = v

        @property
        def pixel_rect(self):
            return pygame.Rect((0, 0), Window.size)

        @property
        def center(self):
            w, h = Window.size
            return Vec(w / 2, h / 2)

        @property
        def resizable(self):
            return _internal._win.resizable

        @resizable.setter
        def resizable(self, v):
            _internal._win.resizable = v

        @property
        def borderless(self):
            return _internal._win.borderless

        @borderless.setter
        def borderless(self, v):
            _internal._win.borderless = v

    class _TimeType(type):
        @property
        def fps(self):
            return _internal._clock.get_fps()

        @property
        def systime(self):
            return _time.time()

        @property
        def syscounter(self):
            return _time.perf_counter()

    class _BindCode:
        def __init__(self, type, code, direction):
            self.type, self.code, self.direction = type, code, direction

        def _check_frame(self):
            if self.type == KEYBOARD:
                status = Frame.keys[self.code]
                if self.direction == PRESS and status:
                    return True
                elif self.direction == RELEASE and not status:
                    return True
            elif self.type == MOUSE:
                status = Frame.buttons[self.code - 1]
                if self.direction == PRESS and status:
                    return True
                elif self.direction == RELEASE and not status:
                    return True
            return False

        def _check_event(self):
            if self.type == KEYBOARD:
                pressed = Frame.keys_just_pressed[self.code]
                released = Frame.keys_just_released[self.code]
                if self.direction == PRESS and pressed:
                    return True
                elif self.direction == RELEASE and released:
                    return True
            elif self.type == MOUSE:
                pressed = Frame.buttons_just_pressed[self.code - 1]
                released = Frame.buttons_just_released[self.code - 1]
                if self.direction == PRESS and pressed:
                    return True
                elif self.direction == RELEASE and released:
                    return True
            return False

    class _Bind:
        def __init__(self, main, *alts):
            self.main, self.alts = main, list(alts)

        def _check_frame(self):
            if self.main._check_frame():
                return True
            for alt in self.alts:
                if alt._check_frame():
                    return True
            return False

        def _check_event(self):
            if self.main._check_event():
                return True
            for alt in self.alts:
                if alt._check_event():
                    return True
            return False

    class _RenderGroup:
        def __init__(self, shader, layer, static, sortmode):
            self._shader, self._layer, self._static, self._sortmode = (
                shader,
                layer,
                static,
                sortmode,
            )
            _internal._LayerGroup._set_render_group(layer, shader, self, static)
            self._reserved_len = 10
            self._entities = []
            self._dirty = False

        def _reset(self):
            self._entities = []
            self._reserved_len = 10
            self._dirty = True

        @staticmethod
        def _exist_create(layer, shader, static, sortmode):
            shader_group = _internal._layer_groups[layer]._shader_groups[shader]
            if static:
                if not shader_group._static_rg:
                    _internal._RenderGroup(shader, layer, static, sortmode)
            else:
                if not shader_group._dynamic_rg:
                    _internal._RenderGroup(shader, layer, static, sortmode)

        @staticmethod
        def _get(layer, shader, static):
            shader_group = _internal._layer_groups[layer]._shader_groups[shader]
            if static:
                return shader_group._static_rg
            else:
                return shader_group._dynamic_rg

        def _make_buffers(self):
            if not _internal._scene_init_complete:
                return
            self._ibo = _internal._gl_context.buffer(
                _internal._RenderGroup._rect_indices(self._reserved_len), dynamic=False
            )
            self._vbo = _internal._gl_context.buffer(
                reserve=self._reserved_len * 4 * 4 * 9, dynamic=True
            )
            self._vao = _internal._gl_context.vertex_array(
                _internal._shaders[self._shader],
                [(self._vbo, "2f 4f 2f 1f", "vPos", "vCol", "vUV", "vTexID")],
                index_buffer=self._ibo,
            )

        @staticmethod
        def _uvs_atlas(aw, ah, w, h, x, y):
            return [
                (x / aw, y / ah),
                ((x + w) / aw, y / ah),
                (x / aw, (y + h) / ah),
                ((x + w) / aw, (y + h) / ah),
            ]

        @staticmethod
        def _rect_indices(amount):
            res = []
            offset = 0
            for _ in range(amount):
                res += [
                    0 + offset,
                    1 + offset,
                    2 + offset,
                    2 + offset,
                    1 + offset,
                    3 + offset,
                ]
                offset += 4
            return _np.fromiter(res, dtype=_np.uint32)

        def _add(self, entity):
            self._entities.append(entity)
            if len(self._entities) >= self._reserved_len:
                self._reserved_len += 10
                self._make_buffers()
            self._dirty = True

        def _remove(self, entity):
            self._entities.remove(entity)
            if self._reserved_len - len(self._entities) > 10:
                self._reserved_len -= 10
                self._make_buffers()
            self._dirty = True

        def _update_render(self):
            if not self._static or self._dirty:
                dirty = False
                data = []
                entities = self._entities
                if self._sortmode == TOPDOWN_SORT:
                    entities = sorted(
                        self._entities, key=lambda x: x._meta_["rect"].bottom
                    )
                for e in entities:
                    if e._meta_["dirty"]:
                        e._meta_["render_data"] = (
                            _internal._RenderGroup._entity_render_data(e)
                        )
                        dirty = True
                    data += e._meta_["render_data"]
                if not self._static or dirty or self._dirty:
                    amount = self._reserved_len - len(self._entities)
                    if amount > 0:
                        data.extend([0] * (amount * 4 * 9))
                    self._vbo.write(_np.fromiter(data, _np.float32))
            self._vao.render()
            self._dirty = False

        @staticmethod
        def _entity_render_data(entity):
            meta = entity._meta_
            rect = meta["rect"]
            tx, ty, sx, sy = rect.left, rect.top, rect.w, rect.h
            if (angle := meta["angle"]) != 0:
                a = math.radians(angle)
                sx2, sy2 = sx / 2, sy / 2
                cx, cy = (tx + sx2, ty + sy2)
                cos, sin = math.cos(a), math.sin(a)
                sx2cos, sx2sin, sy2cos, sy2sin = (
                    sx2 * cos,
                    sx2 * sin,
                    sy2 * cos,
                    sy2 * sin,
                )
                pos0, pos1, pos2, pos3 = (
                    (-sx2cos + sy2sin + cx, -sx2sin - sy2cos + cy),
                    (sx2cos + sy2sin + cx, sx2sin - sy2cos + cy),
                    (-sx2cos - sy2sin + cx, -sx2sin + sy2cos + cy),
                    (sx2cos - sy2sin + cx, sx2sin + sy2cos + cy),
                )
            else:
                pos0, pos1, pos2, pos3 = (
                    (tx, ty),
                    (tx + sx, ty),
                    (tx, ty + sy),
                    (tx + sx, ty + sy),
                )
            uvs, flip = _internal._atlas["uvs"][meta["image"]], meta["flip"]
            if flip[0]:
                uvs = [uvs[1], uvs[0], uvs[3], uvs[2]]
            if flip[1]:
                uvs = [uvs[2], uvs[3], uvs[0], uvs[1]]
            uv0, uv1, uv2, uv3 = uvs
            color = meta["color"]
            return (
                *pos0,
                *color,
                *uv0,
                0,
                *pos1,
                *color,
                *uv1,
                0,
                *pos2,
                *color,
                *uv2,
                0,
                *pos3,
                *color,
                *uv3,
                0,
            )

    class _FontGroup:
        def __init__(self, shader, layer):
            self._shader, self._layer = shader, layer
            _internal._LayerGroup._set_font_group(layer, shader, self)
            self._reserved_len = 100
            self._data = []
            self._dirty = False
            self._make_buffers()

        def _reset(self):
            self._data = []
            self._reserved_len = 100
            self._dirty = True

        def _update_render(self):
            if self._dirty:
                self._dirty = False
                amount = self._reserved_len * 4 * 9 - len(self._data)
                if amount > 0:
                    self._data.extend([0] * amount)
                self._vbo.write(_np.fromiter(self._data, _np.float32))
                self._data = []
            self._vao.render()

        def _make_buffers(self):
            if not _internal._scene_init_complete:
                return
            self._ibo = _internal._gl_context.buffer(
                _internal._RenderGroup._rect_indices(self._reserved_len), dynamic=False
            )
            self._vbo = _internal._gl_context.buffer(
                reserve=self._reserved_len * 4 * 4 * 9, dynamic=True
            )
            self._vao = _internal._gl_context.vertex_array(
                _internal._shaders[self._shader],
                [(self._vbo, "2f 4f 2f 1f", "vPos", "vCol", "vUV", "vTexID")],
                index_buffer=self._ibo,
            )

        def _add_data(self, data):
            self._data += data
            if len(self._data) >= self._reserved_len * 4 * 9:
                self._reserved_len += 100
                self._make_buffers()
            self._dirty = True

        @staticmethod
        def _char_data(topleft, size, color, uvs):
            tx, ty = topleft
            sx, sy = size
            pos0, pos1, pos2, pos3 = (
                (tx, ty),
                (tx + sx, ty),
                (tx, ty + sy),
                (tx + sx, ty + sy),
            )
            uv0, uv1, uv2, uv3 = uvs
            return (
                *pos0,
                *color,
                *uv0,
                1,
                *pos1,
                *color,
                *uv1,
                1,
                *pos2,
                *color,
                *uv2,
                1,
                *pos3,
                *color,
                *uv3,
                1,
            )

        @staticmethod
        def _render_check(
            font_name, position_name, color, layer, shader, max_width, align
        ):
            if color is None:
                color = (1, 1, 1, 1)
            if len(color) == 3:
                color = (*color, 1)
            elif len(color) != 4:
                raise PGLError("Text color must have 4 components")
            if position_name not in [
                "center",
                "tl",
                "bl",
                "tr",
                "br",
                "ml",
                "mr",
                "mb",
                "mt",
            ]:
                raise PGLError(f"Invalid text position name '{position_name}'")
            if font_name not in _internal._fonts_data:
                raise PGLError(f"Font '{font_name}' does not exist")
            if align not in ["center", "left", "right"]:
                raise PGLError(f"Invalid text alignment '{align}'")
            if max_width < 0:
                raise PGLError("Max text width must be >= 0")
            _internal._LayerGroup._exist_create(layer)
            font_group = _internal._FontGroup._exist_create(layer, shader)
            return color, _internal._fonts_data[font_name], font_group

        @staticmethod
        def _exist_create(layer, shader):
            shader_group = _internal._layer_groups[layer]._shader_groups[shader]
            if not shader_group._font_group:
                return _internal._FontGroup(shader, layer)
            return shader_group._font_group

        @staticmethod
        def _char_pos(char, position_name, position, w, h):
            if position_name == "tl":
                char[1] += position[0]
                char[2] += position[1]
            elif position_name == "center":
                char[1] += position[0] - w / 2
                char[2] += position[1] - h / 2
            elif position_name == "tr":
                char[1] += position[0] - w
                char[2] += position[1]
            elif position_name == "bl":
                char[1] += position[0]
                char[2] += position[1] - h
            elif position_name == "br":
                char[1] += position[0] - w
                char[2] += position[1] - h
            elif position_name == "ml":
                char[1] += position[0]
                char[2] += position[1] - h / 2
            elif position_name == "mb":
                char[1] += position[0] - w / 2
                char[2] += position[1] - h
            elif position_name == "mr":
                char[1] += position[0] - w
                char[2] += position[1] - h / 2
            elif position_name == "mt":
                char[1] += position[0] - w / 2
                char[2] += position[1]

    class _LayerGroup:
        def __init__(self, layer):
            self._layer = layer
            self._shader_groups = {
                shader: _internal._ShaderGroup(shader)
                for shader in _internal._SHADER_SOURCE.keys()
            }

        def _exist_create(layer):
            if layer not in _internal._layer_groups:
                _internal._layer_groups[layer] = _internal._LayerGroup(layer)

        def _set_render_group(layer, shader, render_group, static):
            shader_group = _internal._layer_groups[layer]._shader_groups[shader]
            if static:
                shader_group._static_rg = render_group
            else:
                shader_group._dynamic_rg = render_group

        def _set_font_group(layer, shader, font_group):
            shader_group = _internal._layer_groups[layer]._shader_groups[shader]
            shader_group._font_group = font_group

        def _apply_reset():
            for _, layer_group in _internal._layer_groups.items():
                for _, shader_group in layer_group._shader_groups.items():
                    shader_group._reset()

        def _apply_make_buffers():
            for _, layer_group in _internal._layer_groups.items():
                for _, shader_group in layer_group._shader_groups.items():
                    shader_group._make_buffers()

        def _sorted_update_render():
            for _, layer_group in sorted(
                _internal._layer_groups.items(), key=lambda lg: lg[0]
            ):
                for _, shader_group in layer_group._shader_groups.items():
                    shader_group._update_render()

    class _ShaderGroup:
        def __init__(self, shader):
            self._shader = shader
            self._dynamic_rg = None
            self._static_rg = None
            self._font_group = None

        def _make_buffers(self):
            for g in [self._dynamic_rg, self._static_rg, self._font_group]:
                if g:
                    g._make_buffers()

        def _reset(self):
            for g in [self._dynamic_rg, self._static_rg, self._font_group]:
                if g:
                    g._reset()

        def _update_render(self):
            for g in [self._dynamic_rg, self._static_rg, self._font_group]:
                if g:
                    g._update_render()

    class _SoundsType(type):
        @property
        def volume(self):
            return _internal._sound_volume

        @volume.setter
        def volume(self, v):
            _internal._sound_volume = v
            for sound in _internal._sounds.values():
                sound._update_volume()

    class _MusicsType(type):
        @property
        def volume(self):
            return _internal._music_volume

        @volume.setter
        def volume(self, v):
            _internal._music_volume = v
            if _internal._music_playing is not None:
                pygame.mixer.music.set_volume(
                    _internal._music_volume
                    * _internal._musics[_internal._music_playing]["volume"]
                )

        @property
        def playing(self):
            return _internal._music_playing

    class _Ease:
        def get(self, t):
            return self.__call__(t)

    class _EaseN(_Ease):
        def __init__(self, n=2):
            if n < 1:
                raise PGLError("n argument must be >= 1")
            self.n = n


class Sounds(metaclass=_internal._SoundsType):
    def play(name, loops=0, fade_ms=0, stop=False):
        if name not in _internal._sounds:
            raise PGLError(f"Sound '{name}' does not exist")
        _internal._sounds[name]._play(stop, loops, fade_ms)

    def stop(name):
        if name not in _internal._sounds:
            raise PGLError(f"Sound '{name}' does not exist")
        _internal._sounds[name]._stop()

    def set_sound_volume(name, volume):
        if name not in _internal._sounds:
            raise PGLError(f"Sound '{name}' does not exist")
        _internal._sounds[name]._volume = volume
        _internal._sounds[name]._update_volume()

    def get_sound_volume(name):
        if name not in _internal._sounds:
            raise PGLError(f"Sound '{name}' does not exist")
        return _internal._sounds[name]._volume

    def get_sound_objects(name):
        if name not in _internal._sounds:
            raise PGLError(f"Sound '{name}' does not exist")
        return list(_internal._sounds[name]._pg_sounds)

    def add(name, volume, *paths):
        _internal._sounds[name] = _internal._SoundAsset(paths, volume)


class Musics(metaclass=_internal._MusicsType):
    def play(name, loops=-1, start=0, fade_ms=0):
        if name not in _internal._musics:
            raise PGLError(f"Music '{name}' does not exist")
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.music.load(_internal._musics[name]["path"])
        pygame.mixer.music.play(loops, start, fade_ms)

    def pause():
        if _internal._music_playing is None:
            raise PGLError("Cannot pause music if it's not playing")
        pygame.mixer.music.pause()

    def resume():
        if _internal._music_playing is None:
            raise PGLError("Cannot resume music if it never started playing")
        pygame.mixer.music.unpause()

    def stop():
        pygame.mixer.music.stop()
        _internal._music_playing = None

    def set_music_volume(name, volume):
        if name not in _internal._musics:
            raise PGLError(f"Music '{name}' does not exist")
        _internal._musics[name]["volume"] = volume
        if _internal._music_playing == name:
            pygame.mixer.music.set_volume(_internal._music_volume * volume)

    def get_music_volume(name):
        if name not in _internal._musics:
            raise PGLError(f"Music '{name}' does not exist")
        return _internal._musics[name]["volume"]

    def add(name, path, volume=1):
        _internal._musics[name] = {"volume": volume, "path": path}

    def get_music_path(name):
        if name not in _internal._musics:
            raise PGLError(f"Music '{name}' does not exist")
        return _internal._musics[name]["path"]


class Font(_internal._StaticType):
    def clear(layer=0, shader=UI_SHADER):
        _internal._LayerGroup._exist_create(layer)
        font_group = _internal._FontGroup._exist_create(layer, shader)
        font_group._data = []
        font_group._dirty = True

    def render_center(
        font_name, text, position, color=None, scale=1, layer=0, shader=UI_SHADER
    ):
        color, data, font_group = _internal._FontGroup._render_check(
            font_name, "center", color, layer, shader, 0, "center"
        )
        x = y = w = h = 0
        all_chars = []
        for char in text:
            if f"{font_name}_{char}" not in _internal._font_atlas["uvs"]:
                raise PGLError(
                    f"Character '{char}' of font '{font_name}' was not registered"
                )
            cw = data["chars_w"][char] * scale
            all_chars.append([char, x, y, cw])
            x += cw
        w = x
        h = y + data["height"] * scale
        for char in all_chars:
            font_group._add_data(
                _internal._FontGroup._char_data(
                    (char[1] + position[0] - w / 2, char[2] + position[1] - h / 2),
                    (char[3], data["height"] * scale),
                    color,
                    _internal._font_atlas["uvs"][f"{font_name}_{char[0]}"],
                )
            )
        return Vec(w, h)

    def render(
        font_name,
        text,
        position,
        position_name=TEXTPOS_CENTER,
        color=None,
        scale=1,
        layer=0,
        shader=UI_SHADER,
    ):
        color, data, font_group = _internal._FontGroup._render_check(
            font_name, position_name, color, layer, shader, 0, "center"
        )
        x = y = w = h = 0
        all_chars = []
        for char in text:
            if f"{font_name}_{char}" not in _internal._font_atlas["uvs"]:
                raise PGLError(
                    f"Character '{char}' of font '{font_name}' was not registered"
                )
            cw = data["chars_w"][char] * scale
            all_chars.append([char, x, y, cw])
            x += cw
        w = x
        h = y + data["height"] * scale
        for char in all_chars:
            _internal._FontGroup._char_pos(char, position_name, position, w, h)
            font_group._add_data(
                _internal._FontGroup._char_data(
                    (char[1], char[2]),
                    (char[3], data["height"] * scale),
                    color,
                    _internal._font_atlas["uvs"][f"{font_name}_{char[0]}"],
                )
            )
        return Vec(w, h)

    def render_lines(
        font_name,
        text,
        position,
        position_name=TEXTPOS_CENTER,
        max_width=0,
        color=None,
        align=ALIGN_CENTER,
        scale=1,
        layer=0,
        shader=UI_SHADER,
        words_intact=True,
    ):
        color, data, font_group = _internal._FontGroup._render_check(
            font_name, position_name, color, layer, shader, max_width, align
        )
        x = y = w = h = 0
        chars, lines, all_chars = [], [], []
        for char in text:
            if (
                char != "\n"
                and f"{font_name}_{char}" not in _internal._font_atlas["uvs"]
            ):
                raise PGLError(
                    f"Character '{char}' of font '{font_name}' was not registered"
                )
            cw = data["chars_w"].get(char, 0) * scale
            if char == "\n" or (x + cw > max_width and max_width > 0):
                if (not words_intact and char != " ") or char == "\n":
                    if x > w:
                        w = x
                    x = 0
                    y += data["height"] * scale
                    lines.append(chars)
                    all_chars += chars
                    chars = []
            if char == "\n":
                continue
            chars.append([char, x, y, cw])
            x += cw
        if x > w:
            w = x
        if len(chars) > 0:
            all_chars += chars
            lines.append(chars)
        h = y + data["height"] * scale
        if align == "center":
            for line in lines:
                lw = sum([c[3] for c in line])
                offset = w / 2 - lw / 2
                for c in line:
                    c[1] += offset
        elif align == "right":
            for line in lines:
                lw = sum([c[3] for c in line])
                offset = w - lw
                for c in line:
                    c[1] += offset
        for char in all_chars:
            _internal._FontGroup._char_pos(char, position_name, position, w, h)
            font_group._add_data(
                _internal._FontGroup._char_data(
                    (char[1], char[2]),
                    (char[3], data["height"] * scale),
                    color,
                    _internal._font_atlas["uvs"][f"{font_name}_{char[0]}"],
                )
            )
        return Vec(w, h)


class Light:
    def __init__(self, position, color, range, intensity, visible=True):
        self.rect = Rect(0, 0, range, range).move_to(center=position)
        self.color = color
        if len(self.color) > 3:
            raise PGLError("Light color must not contain alpha values")
        self.intensity = intensity
        self.visible = visible
        _internal._lights.append(self)

    @property
    def position(self):
        return Vec(self.rect.center)

    @position.setter
    def position(self, v):
        self.rect.center = v

    @property
    def range(self):
        return self.rect.w

    @range.setter
    def range(self, v):
        c = self.rect.center
        self.rect.w = v
        self.rect.h = v
        self.rect.center = c

    def destroy(self):
        _internal._lights.remove(self)

    def __str__(self):
        return f"Light({self.rect.center}, color={self.color}, range={self.rect.w}, intensity={self.intensity}, visible={self.visible})"

    __repr__ = __str__


class EaseLinear(_internal._Ease):
    def __call__(self, t):
        return t


class EaseIn(_internal._EaseN):
    def __call__(self, t):
        return t**self.n


class EaseOut(_internal._EaseN):
    def __call__(self, t):
        return 1 - (1 - t) ** self.n


class EaseInCirc(_internal._EaseN):
    def __call__(self, t):
        return 1 - math.sqrt(1 - t**self.n)


class EaseOutCirc(_internal._EaseN):
    def __call__(self, t):
        return math.sqrt(1 - (1 - t) ** self.n)


class EaseInSin(_internal._EaseN):
    def __call__(self, t):
        return 1 - math.cos(t * 0.5 * math.pi) ** (1 / self.n)


class EaseOutSin(_internal._EaseN):
    def __call__(self, t):
        return math.sin(t * 0.5 * math.pi) ** (1 / self.n)


class EaseInOutSin(_internal._Ease):
    def __call__(self, t):
        return -math.cos(t * math.pi) / 2 + 0.5


class EaseOvershoot(_internal._Ease):
    def __call__(self, t):
        return 1 - math.cos(4 * math.pi * t) * (1 - t)


class EaseBounce(_internal._Ease):
    def __call__(self, t):
        if 2 * t - 2 == 0:
            return (1 - t) * abs(math.sin(0))
        return (1 - t) * abs(math.sin(math.pi / (2 * t - 2)))


class Animation:
    def __init__(self, value_type=ANIMTYPE_NUMBER, easing=None):
        if easing is None:
            easing = EaseLinear()
        self.value_type = value_type
        self.easing = easing
        self.active = False
        self.value = None
        _internal._animations.append(self)
        self.start(None, None, 0).stop()

    def start(self, start_value, end_value, duration, on_end=None):
        self.on_end = on_end
        self.active = True
        self.start_value, self.end_value = start_value, end_value
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        if self.value_type == ANIMTYPE_COLOR:
            self.start_value = pygame.Color(self.start_value)
            self.end_value = pygame.Color(self.end_value)
        return self

    def stop(self):
        self.active = False
        self.value = self.end_value
        return self

    def update_value(self):
        if not self.active:
            self.value = self.end_value
            return self.end_value

        if not isinstance(self.easing, _internal._Ease):
            raise PGLError(
                f"Animation easing must be of type Ease, not '{type(self.easing)}'"
            )

        if self.value_type == ANIMTYPE_NUMBER:
            self.value = pygame.math.lerp(
                self.start_value,
                self.end_value,
                self.easing(self.get_time() / self.duration),
            )
            if abs(self.value - self.end_value) <= 0.001:
                self.value = self.end_value
                self.active = False
                if self.on_end:
                    self.on_end()

        elif self.value_type == ANIMTYPE_COLOR:
            self.value = self.start_value.lerp(
                self.end_value,
                pygame.math.clamp(
                    self.easing(self.get_time() / self.duration), 0.0, 1.0
                ),
            )
            if (
                abs(self.end_value.r - self.value.r) <= 1
                and abs(self.end_value.g - self.value.g) <= 1
                and abs(self.end_value.b - self.value.b) <= 1
                and abs(self.end_value.a - self.value.a) <= 1
            ):
                self.value = self.end_value
                self.active = False
                if self.on_end:
                    self.on_end()

        elif self.value_type == ANIMTYPE_SEQUENCE:
            new_seq = []
            finished = 0
            if len(self.start_value) != len(self.end_value):
                raise PGLError(
                    "A sequence animation must have start_value and end_value of the same length"
                )
            ease = self.easing(self.get_time() / self.duration)
            for i, val in enumerate(self.start_value):
                endv = self.end_value[i]
                new_val = pygame.math.lerp(val, endv, ease)
                if abs(new_val - endv) <= 0.001:
                    finished += 1
                new_seq.append(new_val)
            new_seq = type(self.start_value)(new_seq)
            self.value = new_seq
            if finished >= len(self.start_value):
                self.active = False
                self.value = self.end_value
                if self.on_end:
                    self.on_end()
        else:
            raise PGLError(
                f"Unknown animation value type '{self.value_type}', available number, sequence and color"
            )
        return self.value

    def destroy(self):
        if self in _internal._animations:
            _internal._animations.remove(self)

    def get_time(self):
        if not self.active:
            return -1
        return (pygame.time.get_ticks() - self.start_time) / 1000


class Binds(_internal._StaticType):
    def check_frame(name):
        if name not in _internal._binds:
            raise PGLError(f"Bind {name} does not exist")
        return _internal._binds[name]._check_frame()

    def check_event(name):
        if name not in _internal._binds:
            raise PGLError(f"Bind {name} does not exist")
        return _internal._binds[name]._check_event()

    def get(name):
        if name not in _internal._binds:
            raise PGLError(f"Bind {name} does not exist")
        bind = _internal._binds[name]
        return _internal._parse_bind(bind.main), [
            _internal._parse_bind(alt) for alt in bind.alts
        ]

    def modify(name, main, *alts):
        if name not in _internal._binds:
            raise PGLError(f"Bind '{name}' does not exist")
        bind = _internal._binds[name]
        bind.main = _internal._parse_bind(main)
        bind.alts = [_internal._parse_bind(alt) for alt in alts]

    def add(name, main, *alts):
        if name in _internal._binds:
            raise PGLError(f"Bind '{name}' already exists")
        main = _internal._parse_bind(main)
        alts = [_internal._parse_bind(alt) for alt in alts]
        _internal._binds[name] = _internal._Bind(main, *alts)

    def remove(name):
        if name not in _internal._binds:
            raise PGLError(f"Bind {name} does not exist")
        _internal._binds.pop(name)


class Camera(_internal._StaticType):
    position = Vec()
    zoom = 1.0
    rect = Rect(0, 0, 0, 0)
    ui_mouse = Vec()
    world_mouse = Vec()
    near_plane = -10000
    far_plane = 10000

    def screen_to_world(screen_pos):
        direction = (screen_pos - Window.center) / Camera.zoom / (_internal._unit / 2)
        return direction + Camera.position

    def screen_to_ui(screen_pos):
        return (screen_pos - Window.center) / (_internal._unit / 2)

    def refresh():
        _internal._update_view()


class Window(_internal._StaticType, metaclass=_internal._WindowType):
    rect = Rect(0, 0, 0, 0)

    def quit():
        _internal._scene.on_quit()
        pygame.quit()
        sys.exit()


class Frame(_internal._StaticType):
    valid = False
    events = None
    screen_mouse = None
    mouse_rel = None
    mouse_wheel = None
    keys = None
    buttons = None
    keys_just_pressed = None
    keys_just_released = None
    buttons_just_pressed = None
    buttons_just_released = None
    absolute_time = None


class Time(_internal._StaticType, metaclass=_internal._TimeType):
    fps_limit = 0
    delta = 0
    scale = 1
    time = pygame.time.get_ticks() / 1000

    def pause():
        global scale
        scale = 0

    def unpause(new_scale=1):
        global scale
        scale = new_scale


class Timer:
    def __init__(
        self, cooldown, end_callback, start=True, *callback_args, **callback_kwargs
    ):
        self.cooldown = cooldown
        self.end_callback = end_callback
        self.callback_args = callback_args
        self.callback_kwargs = callback_kwargs
        self.start_time = -1
        _internal._timers.append(self)
        if start:
            self.start()

    def start(self):
        self.start_time = Time.time

    def destroy(self):
        _internal._timers.remove(self)

    @property
    def active(self):
        return self.start_time != -1


class NoiseSettings:
    def __init__(
        self,
        octaves=2,
        scale=0.08,
        activation=-0.5,
        activation_dir=NOISE_LT,
        type=NOISE_PERLIN_2D,
        seed=None,
        user_data=None,
        persistence=0.5,
        lacunarity=2,
    ):
        if _internal._noise is None:
            try:
                import noise

                _internal._noise = noise
            except ModuleNotFoundError:
                raise PGLError(
                    "To use the NoiseSettings utility you need to install the noise module"
                )
        if seed is None:
            seed = random.randint(0, 9999)
        (
            self.octaves,
            self.scale,
            self.activation,
            self.activation_dir,
            self.seed,
            self.user_data,
            self.type,
            self.persistence,
            self.lacunarity,
        ) = (
            octaves,
            scale,
            activation,
            activation_dir,
            seed,
            user_data,
            type,
            persistence,
            lacunarity,
        )

    def get(self, coordinate, scale_mul=1):
        if self.type == NOISE_SIMPLEX_2D:
            return _internal._noise.snoise2(
                coordinate * self.scale * scale_mul + self.seed,
                coordinate[1] * self.scale * scale_mul + self.seed,
                self.octaves,
                self.persistence,
                self.lacunarity,
            )
        elif self.type == NOISE_SIMPLEX_3D:
            return _internal._noise.snoise3(
                coordinate[0] * self.scale * scale_mul + self.seed,
                coordinate[1] * self.scale * scale_mul + self.seed,
                coordinate[2] * self.scale * scale_mul + self.seed,
                self.octaves,
                self.persistence,
                self.lacunarity,
            )
        elif self.type == NOISE_PERLIN_1D:
            return _internal._noise.pnoise1(
                coordinate * self.scale * scale_mul + self.seed,
                self.octaves,
                self.persistence,
                self.lacunarity,
            )
        elif self.type == NOISE_PERLIN_2D:
            return _internal._noise.pnoise2(
                coordinate[0] * self.scale * scale_mul + self.seed,
                coordinate[1] * self.scale * scale_mul + self.seed,
                self.octaves,
                self.persistence,
                self.lacunarity,
            )
        elif self.type == NOISE_PERLIN_3D:
            return _internal._noise.pnoise3(
                coordinate[0] * self.scale * scale_mul + self.seed,
                coordinate[1] * self.scale * scale_mul + self.seed,
                coordinate[2] * self.scale * scale_mul + self.seed,
                self.octaves,
                self.persistence,
                self.lacunarity,
            )
        else:
            raise PGLError(f"Noise type '{self.type}' is not supported")

    def check(self, coordinate, scale_mul=1):
        value = self.get(coordinate, scale_mul)
        if self.activation_dir == NOISE_LT:
            return value <= self.activation
        elif self.activation_dir == NOISE_GT:
            return value >= self.activation
        else:
            raise PGLError(
                f"Activation direction '{self.activation_dir}' is not supported"
            )


class Scene:
    name: str
    clear_color = (0, 0, 0, 1)

    def __init_subclass__(cls) -> None:
        cls.name = cls.__name__
        _internal._scenes[cls.name] = cls

    @staticmethod
    def load(name):
        if name not in _internal._scenes:
            raise PGLError(f"Scene {name} does not exist")
        if not _internal._scene_init_complete:
            raise PGLError("Cannot load scene while a scene is already loading")

        _internal._tag_entities = {}
        _internal._update_entities = []
        _internal._scene_init_complete = False
        _internal._lights = []
        _internal._LayerGroup._apply_reset()
        new = _internal._scenes[name]()
        _internal._scene = new
        new.init()
        _internal._scene_init_complete = True
        _internal._LayerGroup._apply_make_buffers()
        return new

    @staticmethod
    def get():
        return _internal._scene

    def init(self): ...

    def on_quit(self): ...

    def can_quit(self):
        return True

    def update(self): ...

    def on_window_resize(self): ...

    def __str__(self):
        return f"{self.name} Scene"

    __repr__ = __str__


class Entity:
    _meta_: dict[str, tuple | Rect | float]
    _meta_subclass_: dict[str]

    @staticmethod
    def with_tag(*tags):
        sets = [
            _internal._tag_entities[tag]
            for tag in tags
            if tag in _internal._tag_entities
        ]
        if len(sets) <= 0:
            return list()
        if len(sets) == 1:
            return list(sets[0])
        return list(sets[0].intersection(*sets[1:]))

    def __init_subclass__(
        subclass,
        flags=None,
        tags=None,
        layer=0,
        size=None,
        shader=UNLIT_SHADER,
        image=None,
        flip=None,
    ):
        if flags is None:
            flags = tuple()
        if tags is None:
            tags = tuple()
        if size is None:
            size = (1, 1)
        if image is None:
            image = "square"
        if flip is None:
            flip = (False, False)
        subclass._meta_subclass_ = {
            "flags": flags,
            "tags": tags,
            "size": size,
            "layer": layer,
            "shader": shader,
            "static": STATIC in flags,
            "image": image,
            "flip": flip,
        }
        if INVISIBLE in flags:
            return
        sortmode = "none"
        if TOPDOWN_SORT in flags:
            sortmode = TOPDOWN_SORT
        _internal._LayerGroup._exist_create(layer)
        _internal._RenderGroup._exist_create(layer, shader, STATIC in flags, sortmode)

    @classmethod
    def new(
        cls,
        position=None,
        size=None,
        angle=None,
        color=None,
        image=None,
        flip=None,
        containers=None,
        name="entity",
    ):
        if not hasattr(cls, "_meta_subclass_"):
            raise PGLError(
                "Entity cannot be instantiated, you can only instantiate subclasses"
            )
        new = cls()
        new.name = name
        metasub = cls._meta_subclass_
        flags = metasub["flags"]
        if position is None:
            position = (0, 0)
        if angle is None:
            angle = 0
        if size is None:
            size = metasub["size"]
        if color is None:
            color = (1, 1, 1, 1)
        if image is None:
            image = metasub["image"]
        if containers is None:
            containers = ()
        if len(color) == 3:
            color = (*color, 1)
        if flip is None:
            flip = metasub["flip"]
        group = None

        for tag in metasub["tags"]:
            if tag not in _internal._tag_entities:
                _internal._tag_entities[tag] = set()
            _internal._tag_entities[tag].add(new)
        if UPDATE in flags:
            _internal._update_entities.append(new)
        if INVISIBLE not in flags:
            group = _internal._RenderGroup._get(
                metasub["layer"], metasub["shader"], STATIC in flags
            )
            group._add(new)

        new._meta_ = {
            "tags": tuple(metasub["tags"]),
            "rect": Rect((0, 0), size).move_to(center=position),
            "angle": angle,
            "color": color,
            "image": image,
            "flip": flip,
            "group": group,
            "dirty": True,
            "render_data": None,
            "conts": [],
            "update": UPDATE in flags,
            "alive": True,
        }
        for cont in containers:
            cont.add(new)
        new.init()
        return new

    def destroy(self):
        if not self._meta_["alive"]:
            return
        self.on_destroy()
        self._meta_["dirty"] = True
        self._meta_["alive"] = False
        for tag in self._meta_["tags"]:
            if self in _internal._tag_entities[tag]:
                _internal._tag_entities[tag].remove(self)
        if self._meta_["update"]:
            _internal._update_entities.remove(self)
        for cont in list(self._meta_["conts"]):
            cont.remove(self)
        if self._meta_["group"] is not None:
            self._meta_["group"]._remove(self)

    def update(self): ...

    def init(self): ...

    def setup(self):
        return self

    def on_destroy(self): ...

    @property
    def tags(self):
        return tuple(self._meta_["tags"])

    @property
    def position(self):
        return Vec(self._meta_["rect"].center)

    @position.setter
    def position(self, v):
        self._meta_["rect"].center = v
        self._meta_["dirty"] = True
        if self._meta_subclass_["static"] and (g := self._meta_["group"]):
            g._dirty = True

    @property
    def size(self):
        return Vec(self._meta_["rect"].size)

    @size.setter
    def size(self, v):
        self._meta_["rect"].size = v
        self._meta_["dirty"] = True
        if self._meta_subclass_["static"] and (g := self._meta_["group"]):
            g._dirty = True

    @property
    def angle(self):
        return self._meta_["angle"]

    @angle.setter
    def angle(self, v):
        self._meta_["angle"] = v
        self._meta_["dirty"] = True
        if self._meta_subclass_["static"] and (g := self._meta_["group"]):
            g._dirty = True

    @property
    def color(self):
        return self._meta_["color"]

    @color.setter
    def color(self, v):
        if len(v) == 3:
            v = (*v, 1)
        elif len(v) != 4:
            raise PGLError("Color value must have 3 or 4 components")
        self._meta_["color"] = v
        self._meta_["dirty"] = True
        if self._meta_subclass_["static"] and (g := self._meta_["group"]):
            g._dirty = True

    @property
    def image(self):
        return self._meta_["image"]

    @image.setter
    def image(self, v):
        if v is None:
            v = "square"
        elif v not in _internal._atlas["uvs"]:
            raise PGLError(f"Image {v} does not exist")
        self._meta_["image"] = v
        self._meta_["dirty"] = True
        if self._meta_subclass_["static"] and (g := self._meta_["group"]):
            g._dirty = True

    @property
    def flip(self):
        return self._meta_["flip"]

    @flip.setter
    def flip(self, v):
        self._meta_["flip"] = v
        self._meta_["dirty"] = True
        if self._meta_subclass_["static"] and (g := self._meta_["group"]):
            g._dirty = True

    @property
    def rect(self):
        return self._meta_["rect"].copy()

    @rect.setter
    def rect(self, v):
        self._meta_["rect"] = v.copy()

    @property
    def containers(self):
        return list(self._meta_["conts"])

    @property
    def forward(self):
        return Vec(0, -1).rotate(self._meta_["angle"])

    @property
    def alive(self):
        return self._meta_["alive"]

    def __str__(self):
        if self.name != "entity":
            if len(self.tags) > 0:
                return f"{self.__class__.__name__}(name={self.name}, tags={self.tags})"
            return f"{self.__class__.__name__}(name={self.name})"
        if len(self.tags) > 0:
            return f"{self.__class__.__name__}(tags={self.tags})"
        return f"{self.__class__.__name__}"

    __repr__ = __str__


class Container:
    def __init__(self, *entities):
        _internal._cont_entities[id(self)] = []
        self.add(*entities)

    def add(self, *entities):
        _internal._cont_entities[id(self)].extend(entities)
        for entity in entities:
            entity._meta_["conts"].append(self)

    def remove(self, *entities):
        _entities = _internal._cont_entities[id(self)]
        for entity in entities:
            try:
                _entities.remove(entity)
                entity._meta_["conts"].remove(self)
            except ValueError:
                ...

    def get(self):
        return list(_internal._cont_entities[id(self)])

    def has(self, entity):
        return self in entity._meta_["conts"]

    def empty(self):
        for entity in _internal._cont_entities[id(self)]:
            entity._meta_["conts"].remove(self)
        _internal._cont_entities[id(self)] = []

    def destroy(self):
        self.empty()
        _internal._cont_entities.pop(id(self))

    def destroy_entities(self):
        for entity in list(_internal._cont_entities[id(self)]):
            entity.destroy()

    def __del__(self):
        self.destroy()

    def __len__(self):
        return len(_internal._cont_entities[id(self)])

    def __contains__(self, value):
        return self in value._meta_["conts"]

    def __iter__(self):
        yield from self.get()

    def __getitem__(self, idx):
        return _internal._cont_entities[id(self)][idx]

    def __str__(self):
        return f"Container ({len(_internal._cont_entities[id(self)])} entities)"

    __repr__ = __str__


class frange:
    def __init__(self, start, stop, step):
        self.start, self.stop, self.step = start, stop, step

    def __iter__(self):
        value = self.start
        while value <= self.stop:
            yield value
            value += self.step


def custom_image_loader(func):
    _internal._custom_image_loaders.append(func)
    return func


def custom_image_canvas(size=(100, 100)):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(0)
    return surf


def light_filter(func):
    _internal._light_filter = func
    return func


def from_pg_color(color, alpha=True):
    color = pygame.Color(color)
    if alpha:
        return (color.r / 255, color.g / 255, color.b / 255, color.a / 255)
    else:
        return (color.r / 255, color.g / 255, color.b / 255)
