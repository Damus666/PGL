import typing

if not typing.TYPE_CHECKING:
    raise RuntimeError(
        "prelude.pyi is a stub file and shoud not be imported. The only way to import it is to type 'from prelude import *' in your files. If you imported it differently it won't work"
    )

import pygame
import sys
import os
import random
import math

Rect = pygame.Rect
Vec = pygame.Vector2
STATIC = "static"
UPDATE = "update"
INVISIBLE = "invisible"
KEYBOARD = "key"
MOUSE = "mouse"
PRESS = "press"
RELEASE = "release"
UNLIT_SHADER = "unlit"
LIT_SHADER = ("lit",)
UI_SHADER = ("ui",)
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


class Entity:
    def __init_subclass__(
        cls,
        flags: tuple[str] = (),
        tags: tuple[str] = (),
        size: typing.Sequence[float] = (1, 1),
        layer: int = 0,
        shader: str = UNLIT_SHADER,
        image: str = "square",
        flip: typing.Sequence[bool] = (False, False),
    ): ...

    @classmethod
    def new(
        cls,
        position: typing.Sequence[float] = (0, 0),
        size: typing.Sequence[float] = None,
        angle: float = 0,
        color: tuple[float, float, float, float] = (1, 1, 1, 1),
        image: str = None,
        flip=(False, False),
        containers=(),
    ) -> typing.Self: ...
    @staticmethod
    def with_tag(*tags) -> set[Entity]: ...
    def update(self): ...
    def destroy(self): ...
    def init(self): ...
    def setup(self) -> typing.Self: ...
    def on_destroy(self): ...
    @property
    def angle(self) -> float: ...
    @property
    def position(self) -> Vec: ...
    @property
    def size(self) -> Vec: ...
    @property
    def color(self) -> tuple[float, float, float, float]: ...
    @property
    def image(self) -> str: ...
    @property
    def flip(self) -> tuple[bool, bool]: ...
    @property
    def tags(self) -> tuple[str]: ...
    @property
    def rect(self) -> Rect: ...
    @property
    def containers(self) -> list[Container]: ...
    @property
    def forward(self) -> Vec: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...


class Container:
    def __init__(self, *entities: Entity): ...
    def add(self, *entities: Entity): ...
    def remove(self, *entities: Entity): ...
    def has(self, entity: Entity) -> bool: ...
    def get(self) -> list[Entity]: ...
    def empty(self): ...
    def destroy(self): ...
    def destroy_entities(self): ...
    def __len__(self) -> int: ...
    def __del__(self): ...
    def __contains__(self, value: Entity) -> bool: ...
    def __iter__(self): ...
    def __getitem__(self, index: int) -> Entity: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...


class Scene:
    name: str
    clear_color: tuple[float, float, float, float]
    def update(self): ...
    def can_quit(self) -> bool: ...
    def on_quit(self): ...
    def on_window_resize(self): ...
    @staticmethod
    def get(self) -> "Scene": ...
    @staticmethod
    def load(name: str) -> "Scene": ...


class Time:
    fps_limit: int
    delta: float
    time: float
    systime: float
    syscounter: float
    scale: float
    fps: float
    @staticmethod
    def pause(): ...
    @staticmethod
    def unpause(new_scale: float): ...


class Timer:
    cooldown: float

    def __init__(
        self,
        cooldown: float,
        end_callback: typing.Callable[[], bool],
        start: bool = True,
        *callback_args,
        **callback_kwargs
    ): ...
    def start(self): ...
    @property
    def active(self) -> bool: ...


class Frame:
    events: list[pygame.Event]
    screen_mouse: Vec
    mouse_rel: Vec
    keys = None
    buttons: tuple[int]
    keys_just_pressed = None
    keys_just_released = None
    absolute_time: int
    valid: bool


class Window:
    pixel_rect: Rect
    center: Vec
    size: Vec
    title: str
    resizable: bool
    borderless: bool
    rect: Rect
    @staticmethod
    def quit(): ...


class Camera:
    position: Vec
    zoom: float
    rect: Rect
    ui_mouse: Vec
    world_mouse: Vec
    near_plane: float
    far_plane: float
    @staticmethod
    def screen_to_world(screen_pos: Vec) -> Vec: ...
    @staticmethod
    def screen_to_ui(screen_pos: Vec) -> Vec: ...
    @staticmethod
    def refresh(): ...


class _BindCode:
    type: str
    direction: str
    code: int


class _Bind:
    main: _BindCode
    alts: list[_BindCode]


class Binds:
    @staticmethod
    def check_frame(name: str) -> bool: ...
    @staticmethod
    def check_event(name: str) -> bool: ...
    @staticmethod
    def get(name: str) -> _Bind: ...


class Light:
    rect: Rect
    intensity: float
    color: tuple[float, float, float]
    @property
    def position(self) -> Vec: ...
    @property
    def range(self) -> float: ...

    def __init__(
        self,
        position: typing.Sequence[float],
        color: tuple[float, float, float],
        range: float,
        intensity: float,
    ): ...
    def destroy(self): ...


class Font:
    @staticmethod
    def render_lines(
        font_name: str,
        text: str,
        position: typing.Sequence[float],
        position_name: str = TEXTPOS_CENTER,
        max_width: float = 0,
        color: tuple[float, float, float] = None,
        align: str = ALIGN_CENTER,
        scale: float = 1,
        layer: int = 0,
        shader: str = UI_SHADER,
        words_intact: bool = True,
    ) -> Vec: ...

    @staticmethod
    def render(
        font_name: str,
        text: str,
        position: typing.Sequence[float],
        position_name: str = TEXTPOS_CENTER,
        color: tuple[float, float, float] = None,
        scale: float = 1,
        layer: int = 0,
        shader: str = UI_SHADER,
    ) -> Vec: ...

    @staticmethod
    def render_center(
        font_name: str,
        text: str,
        position: typing.Sequence[float],
        color: tuple[float, float, float] = None,
        scale: float = 1,
        layer: int = 0,
        shader: str = UI_SHADER,
    ) -> Vec: ...

    @staticmethod
    def clear(layer=0, shader=UI_SHADER): ...


def from_pg_color(
    color: str | pygame.Color) -> tuple[float, float, float, float]: ...


def custom_image_loader(
    func: typing.Callable[[], dict[str, pygame.Surface]]
) -> typing.Callable[[], dict[str, pygame.Surface]]: ...


def light_filter(
    func: typing.Callable[[Light], bool]
) -> typing.Callable[[Light], bool]: ...


def custom_image_canvas(size: list[int] = (100, 100)) -> pygame.Surface: ...
