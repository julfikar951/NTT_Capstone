// Box.asm   (K = 29)
// While any key is pressed -> black box; key released -> box disappears.
//
// Box position : starts at row K = 29, 20 rows tall
// Box width    : 16 * ((29 mod 4) + 1) = 32 pixels = 2 words, at the left edge
// First word   : SCREEN + 32*29 = 16384 + 928 = 17312   (rows 29 ... 48)

(LOOP)
    @KBD
    D=M
    @PRESSED
    D;JNE           // key pressed? -> go and draw black

    @color          // no key -> colour = 0 (white)
    M=0
    @PAINT
    0;JMP

(PRESSED)
    @color          // key -> colour = -1 (all 16 bits = 1 = black)
    M=-1

(PAINT)
    @SCREEN
    D=A
    @928            // 32 * 29  (row 29)   <- change this to move the box
    D=D+A
    @addr           // addr = first word of the current row
    M=D

    @20             // 20 rows tall        <- change this for height
    D=A
    @rows
    M=D

(ROW)
    @addr
    D=M
    @ptr            // ptr = word we are painting now
    M=D

    @2              // 2 words per row = 32 pixels   <- change this for width
    D=A
    @cols
    M=D

(COL)
    @color
    D=M
    @ptr
    A=M
    M=D             // paint one word (16 pixels)

    @ptr
    M=M+1           // next word in the same row

    @cols
    MD=M-1
    @COL
    D;JGT           // more words in this row?

    @32
    D=A
    @addr
    M=D+M           // start of next row (+32 words)

    @rows
    MD=M-1
    @ROW
    D;JGT           // more rows left?

    @LOOP           // repaint forever (so key changes are noticed)
    0;JMP
