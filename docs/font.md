## [<- Back](PGL.md)

# Font Rendering

Rendering text is separate from entities making it easier and highly optimized, but uses the same shaders.<br>
Just like the entity render groups, the text is grouped based on the layer and the shader. There can be one group for every layer and shader.<br>
When you call one of the render text functions, the group will become dirty and will update the buffers as soon as possible. Until the functions are called again, the group won't update the buffer for performance.<br>
This means you can use different layers for text that should always change (e.g. FPS counter) and text that will rarely change (e.g. player level).<br>

To manually clear a group in a layer and a shader, you can use the `Font.clear(layer, shader)` static method.<br>
The `Font` static class also contains the following text rendering functions:

- `Font.render()`: Render text on a single line. Parameters:
  - font_name: The font to use, must be present in `config.json`
  - text: The string with text. You can't use newlines, use `Font.render_lines()` instead
  - position: `Sequence[float]`: The text position. The position can point to any corners of the text rect (center, topleft...)
  - position_name: A constant telling how the position should be interpreted. `TEXTPOS_CENTER` will center around the `position` while `TEXTPOS_BR` will put the bottom right of the text on the `position`. Only use those constants
  - color: 4-components tuple, defaults to white.
  - scale: Scale to apply on top of the base scale
  - layer and shader as covered before. Use the SHADER\_ constants for it. Using too many layers is not recommended
- `Font.render_center()`: Exactly like the previous function, but cannot set the position name. Useful because text centering is very common and this will make it more performant
- `Font.render_lines()`: Like `Font.render()` but you can use the new line and have multiple lines. It has extra arguments on top of the rest:
  - max_width: The text width will not exceed this value. If set to 0 (default) it will have no limit
  - words_intact: Flag signaling to keep words together. This will make the width imprecise that could exceed max_width
  - align: A constant ALIGN_CENTER/LEFT/RIGHT to align the lines
