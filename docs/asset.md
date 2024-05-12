## [<- Back](PGL.md)

# Images

All images in the `assets` directory will be loaded and will be available.<br>
The file name corrisponds to the image name.<br>
If you want for an image to be ignored, prefix the name with `ignore`.

## Using pygame for images

Often you want to create images from pygame, and not load them from disk, for example if you want a circle.<br>
With PGL it's very simple to do this:

```py
@custom_image_loader
def my_image_loader():
    surf = custom_image_canvas()
    pygame.draw.circle(surf, "white", (50, 50), 50)
    return {
        "circle": surf
    }
```

Like you can see in the example, you can decorate (as many as you want) your function with `custom_image_loader`. Your function will be called when initializing PGL and all surfaces that the function returns will be added to the images<br>
Your function must return a dictionary `{image_name_string: surface}`<br><br>
`custom_image_canvas(size: tuple[int, int] = (100, 100))` is just a shortcut to create a surface with an alpha channel ready for blitting.

# Scripts

_Use `Vec` and `Rect` instead of `pygame.Vector2` and `pygame.FRect`_

**ALL** the scripts in the project directory will be included in the output file.<br>
All scripts should include the following line:

```py
from prelude import *
```

prelude is a stub file and this line (it must be typed exactly like this) will be omitted in the output file.<br>
`prelude.pyi` will tell your text editor what is available with PGL, it's not needed for the code as every feature will be present in the output file.<br>

## Importing your scripts

Importing your scripts in other scripts is **NOT** necessary because every script will exist in the same output file.<br>
If you want to import something for your text editor's linting, you must do it with the condition below as otherwise it will result in a missing import error on the output file:

```py
from prelude import *
import typing
if typing.TYPE_CHECKING:
    from my_folder.my_script import my_function, MyClass, MY_CONSTANT
```
