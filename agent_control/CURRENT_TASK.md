# Version 5.13 — UI Polish

## Objective

Adjust the layout of the **Refresh Now** button so it no longer stretches across the full window width. The button should appear **centered horizontally** with natural padding around the text.

The button should size itself according to its contents rather than expanding to fill the layout.

## Current Behavior

The **Refresh Now** button is placed directly into a vertical layout, causing it to expand to the full width of the window.

Result:

- Button spans entire window width
- Visual style resembles a status bar rather than a control

## Desired Behavior

The **Refresh Now** button should:

- Be **centered horizontally**
- Maintain **natural padding around the text**
- **Not stretch** across the window
- Resize automatically based on text length
- Maintain the existing click behavior

Example appearance:

```
           [ Refresh Now ]
```

## Implementation Approach

Wrap the button inside a horizontal layout with stretch spacers.

Example layout pattern:

```
stretch | button | stretch
```

## Recommended Implementation

Replace the direct layout insertion with a centered layout container.

Example:

```python
refresh_layout = QHBoxLayout()
refresh_layout.addStretch()
refresh_layout.addWidget(self.refresh_button)
refresh_layout.addStretch()

layout.addLayout(refresh_layout)
```

This keeps the button centered and prevents horizontal expansion.

## Constraints

Do **not** modify:

- Button label
- Button signal connections
- Worker thread refresh logic
- Forecast refresh behavior
- Other layout sections

Only adjust **button positioning**.

## Acceptance Criteria

- Button appears centered horizontally
- Button width adapts to text
- Window resizing does not stretch the button
- Button remains fully functional
- No layout regressions elsewhere in the UI

## Version Notes

Version 5.13 introduces a small UI polish improvement to better match standard desktop application layout conventions.

No changes to functionality or backend logic.
