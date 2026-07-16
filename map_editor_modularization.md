# MAP EDITOR MODULARIZATION

Mission

Split map_editor.py into modules.

The user must not notice any difference.

Only code location may change.

Behavior must remain identical.

------------------------------------------------

WORK ORDER

STEP 1

Inventory.

Before changing anything,
list every

Class

Method

Member Variable

Shortcut

Mouse Event

Draw Function

Serializer

Save

Load

Selection

Camera

Palette

Registry

Inspector

Status Bar

Grid

Trigger

Entity

Platform

STEP 2

Dependency Analysis.

Find

who owns state

who calls whom

execution order

STEP 3

Module Planning.

Assign every function to exactly one module.

No function may disappear.

STEP 4

Copy.

Copy functions first.

Never delete originals.

STEP 5

Reconnect.

Update imports.

Keep behavior identical.

STEP 6

Verification.

Compare original and modularized implementation.

STEP 7

Delete duplicate code only after verification.

------------------------------------------------

MODULE RESPONSIBILITIES

editor_main.py

Only

Lifecycle

Coordination

Global State

No rendering.

No input.

No serialization.

--------------------------------------------

input_handler.py

Keyboard

Mouse

Camera

Snap

Brush

--------------------------------------------

renderer.py

Everything visual.

Grid

Sidebar

Inspector

Status

Selection

Preview

Nothing else.

--------------------------------------------

serializer.py

Save

Load

Serialize

Deserialize

JSON compatibility

--------------------------------------------

selection.py

Selection

Dragging

Hit Test

Delete

--------------------------------------------

object_registry.py

Palette

Definitions

Registry

Metadata

--------------------------------------------

map_selector.py

Map Selection

New Map

Back Button

Map List

--------------------------------------------

event_discover.py

Trigger Discovery

Action Discovery

Dynamic Modules

------------------------------------------------

NEVER

Delete features

Rename APIs

Rewrite systems

Optimize logic

Change UI

Change JSON

Change shortcuts

Change draw order

Change save format

------------------------------------------------

SUCCESS

Only file locations changed.

Everything else remains identical.