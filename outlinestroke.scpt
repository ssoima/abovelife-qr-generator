tell application "Adobe Illustrator"

  activate

          tell the current document

                    set selected of every page item to true

          end tell

end tell

tell application "System Events"

          click menu item "Outline Stroke" of menu "Path" of menu item "Path" of menu "Object" of menu bar item "Object" of menu bar 1 of process "Adobe Illustrator"
end tell