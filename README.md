# Nand to Tetris - Capstone (Make the Computer Draw a Box)

**K = 29**

| Item | Value |
|---|---|
| Box start row | 29 (rows 29-48, 20 rows tall) |
| Box width | 16 x ((29 mod 4) + 1) = 32 pixels (2 words), left edge |
| First screen address | 16384 + 32*29 = 17312 |
| Extra assembler feature (29 mod 3 = 2) | Warning if the same label is written twice |

## Files
- `CPU.hdl`, `Memory.hdl`, `Computer.hdl` - Part A
- `assembler.py` - Part B (two-pass Hack assembler)
- `Box.asm`, `Box.hack` - Part C
- `Add`, `Max`, `Rect`, `Pong` (.asm / .hack) - assembler tests
- `ErrorTest.asm` - program with a duplicate label to show the warning
- `*.png` - test screenshots

## Run
```
python assembler.py Box.asm          # creates Box.hack
python assembler.py ErrorTest.asm    # prints "Warning: Line 7: label 'LOOP' is already defined ..."
```
