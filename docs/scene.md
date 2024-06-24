## [<- Back](PGL.md)

# Scenes

A scene represents a game state like the world or the menu screen.<br>
It's like a mother of all entities which creates them and manages them.<br>
One scene is required to start the game. <br>
You can load a different scene at any time with the `Scene.load(name: str)` static method (where name is the class name).<br>
Use `Scene.get()` to get the currently active scene.<br>

To create a scene, create a new class that inherits from `Scene`.<br>
The scene class will automatically have the `name` attribute (which is the class name) and the `clear_color` attribute which you can change at any time.<br>

The best methods to override are `init()` and `update()`. <br>
update is called every frame, after the timer calls and before any entity update.<br>
The init is called only once, immediately after the scene is loaded which is the best place to create some of your enities.<br>

You can also override `quit()`, called when the window is closing and `on_window_resize()` called when the window resizes (useful for UI anchoring). Finally, the `can_quit()` method should return whether the window _can_ close when the user presses X (`Window.quit()` skips this call)

```py
class Main(Scene):
    def init(self):
        # create entities etc
        print("scene initialized")

    def update(self):
        Window.title = f"{round(Time.fps)}"

    def quit(self):
        print("closing game")
```

# Entities

Entities are the main part of PGL. To create your entity, you have to create a new class that inherits from `Entity`. When you inherit from the entity you should also pass some keywords argument to it, like so:

```py
class MyEntity(Entity, tags=("entity", ), flags=(UPDATE, ), shader=LIT_SHADER):...
```

- flags: a tuple with flags. The flags available are:
  - `UPDATE`: this entity's `update()` method will be called
  - `STATIC`: this entity will rarely change attributes so the GPU shouldn't be updated very often (useful to have hundreds of thousands of tiles at hundreds of FPS)
  - `INVISIBLE`: this entity should not be rendered
  - `TOPDOWN_SORT`: the entities in this layer and with this shader should be sorted using the rect's midbottom
- tags: a tuple with strings, entities with the same tags can be obtained with the `Entity.with_tag(*tags)` static method.
- layer: an int that will render the entities with the same layer on top of entities with a lower layer
- shader: the shader to use for rendering:
  - `LIT_SHADER`: the entity will be illuminated
  - `UNLIT_SHADER`: the entity will always be lit
  - `REPLACE_SHADER`: the color of the entity will override the color of the pixels keeping brightness the same
  - `UI_SHADER`: the entity is not in the world so the camera won't affect it (useful for UI and text)
- size, image, flip: default values when they are not passed to the entity's new method.

Entities with the same layer & shader will be rendered at the same time as a mesh. Those entities must be either all static or all dynamic.<br>

With the entity you get access to this non-overridable methods:

- `YourEntity.new()`: Create a new entity of this type. Parameters are self explainatory. If some values are emitted the defaults from the entity class notation will be used.
- `Entity.with_tag(*tags)`: Return all entities with the given tags
- `destroy()` wipe the entity out of existence removing all references to it

You can also override some methods:

- `update()`: Called every frame if the UPDATE flag is set
- `init()`: Called immediately after it is created
- `setup()`: This should `return self` and can be called sequentially to new to pass extra arguments to the entity. `YourEntity.new((0, 0)).setup(player=True)`
- `on_destroy()`: Called immediately before the entity is destroyed

And you also have properties:<br>

- position: `Vec`
- size: `Vec`
- rect: `Rect`
- angle: `float`
- color: `tuple[float, float, float, float]`
- image: name of a loaded image
- flip: `tuple[bool, bool]` where the first bool is x and the second is y
- tags: `tuple[str]`, read-only
- name: `str`
- containers: `list` of containers the entity is in, read-only
- forward: the `Vec(0, -1)` rotated by the angle
- alive: `bool` stating whether the entity was destroyed or not

## NOTE:

Rect, size, position, flip properties are **COPIES** of the actual value. Doing `entity.position.x = 2` will **NOT** change the position. To modify it correctly you must do `entity.position = Vec(2, entity.position.y)`

# Light

To add a light you just need to instantiate the `Light` class.

The light has the following properties, some available in the constructor:

- position: `Vec`
- range: `float`
- intensity: `float`
- color: `tuple[float, float, float]`
- rect: `Rect`

### NOTE: the light color has only 3 components, not 4 and this time you can mutate the rect attribute but can't mutate the position components

You can also provide a function for filtering lights and not render them. By default, it filters lights which the camera can't see. To tell PGL about your function, use the `light_filter` decorator which you can only use once.

```py
@light_filter
def my_filter(light) -> bool:
    return light.color[0] > 0.5 # the light has enough red
```

# Containers

A container is an extended list useful to group objects together. You can pass some containers to an entity's constructor and it will add itself into them, and you can pass entities to a container constructor and it will add them to iteself. The container has the following methods:

- `add(\*entities)`
- `remove(\*entities)`: remove some entities but does **NOT** destroy them
- `has(entity)` -> `bool`
- `get()` -> `list` of entities, shallow copy
- `empty()`: remove all entities but does **NOT** destroy them. If you want to wipe the entities to add new ones, use `destroy_entities()` instead
- `destroy()`: empty and destroy the container but does **NOT** destroy the entities
- `destroy_entities()`: destroy all the entities but not the container

It also supports the following operations:

- `len(container)` -> amount of entities
- `del container`: empty the container and destroy it
- `entity in container`: same as `container.has(entity)`
- `for entity in container`/`iter(container)`: iterate over the entities
- `container[2]`: get the entity at index 2
