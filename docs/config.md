## [<- Back](PGL.md)

# config.json

This file gives some entry point settings for your game. Those settings will only be applied at the start of it and won't have other effects during runtime.<br>
The `config.json` file can have the following entries:

## `"window"`

The window entry can have the following settings:

- `"title"`: a string with the window title
- `"size"`: a list of integers for the size or the string `"maximized"` (default)
- `"resizable"`: a boolean for the ability to resize the window (default `true`)
- `"borderless"`: a boolean to remove the window border (default `false`)

## `"game"` (required)

The game entry have general settings such as:

- `"start-scene"`: the first scene to be loaded (REQUIRED)
- `"framerate-limit"`: the maximum framerate, expects a number or the string `"unlimited"` (default)
- `"max-lights"`: the maximum numbers of active lights. Can't exceed `145`
- `"ambient-light"`: a STRING with the default lighting when there is no light. Example: `"0.15, 0.15, 0.15, 1"` (default). NOTE: a notation different from this will result in shader compiler errors!

## `"fonts"`

Specifies the fonts to be loaded. Can't be changed during runtime.
Should be a dictionary with `"font name": {font settings}`. Each settings can have this keys:

- `"path"`: string with file path or sysfont name or `null` (default font)
- `"bitmap-size"`: the font size prnted on the texture, higher = more high res for big text. (default `100`)
- `"base-scale"`: the font scaling to apply by default (defalt `1`)
- `"antialias"`: enable antialiasing, not recommended for pixel art fonts (default `true`)
- `"bold"`, `"italic"`, `"underline"`, `"strikethrough"`: style settings (default font). To have more styles for the same font another entry in the dictionary is needed.
- `"chars"`: the characters to load. By default they are the printable ASCII characters but can be overrided for other languages without the latin alphabet.
- `"extra-chars"`: if you don't want to override the chars but need some extra letters like accented ones you can put them in a string here.

Example:

```json
"fonts": {
    "default": {
        "path": null,
        "base-scale": 0.5,
        "extra-chars": "òàèìù"
    }
}
```

## `"binds"`

This dictionary specifies some action names and the keycodes that can trigger them.
You can check for continuous click or single click in code. You can modify this during runtime<br>.
Each entry should be like described below.

### Key code

A keycode is a `list` that must have a specific structure:

- element `0`: the actual key code. Can be an integer or any constant in the pygame module like `"BUTTON_LEFT"` or `"K_SPACE"`
- other elements: can have the string `"release"` and the string `"mouse"`. Release means the action is triggered when the user releases the key while mouse means it's a mouse button and not a keyboard key.

Example: `["K_SPACE", "release"]`, `["BUTTON_MIDDLE", "mouse"]`

### Simple bind

If you only need one key code, you bind can look like this:

```json
"binds": {
    "print": ["K_p"]
}
```

### Multiple bind

If you want more key codes to activate the same action you can do this:

```json
"binds": {
    "left": {
        "main": ["K_a"],
        "alts": [["K_LEFT"], ["K_SPACE"]]
    }
}
```
