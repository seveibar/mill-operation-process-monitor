G90 X0 Y0 Z1

G20
G91
G01 F80

; Calibration
G01 X4
G01 X-4
G4 P2

G01 Y4
G01 Y-4
G4 P2

G01 Z1
G01 Z-1
G4 P2

; Square
G01 X4
G01 Y4
G01 X-4
G01 Y-4
G4 P2

; Triangle
G01 X4 Y4
G01 X-4
G01 Y-4
G4 P2

; Zig Zag
G01 X.5 Y4
G01 X.5 Y-4
G01 X.5 Y4
G01 X.5 Y-4
G01 X.5 Y4
G01 X.5 Y-4
G01 X.5 Y4
G01 X.5 Y-4
G4 P2

; Square Wave
G01 X-.5
G01 Y4
G01 X-.5
G01 Y-4
G01 X-.5
G01 Y4
G01 X-.5
G01 Y-4
G01 X-.5
G01 Y4
G01 X-.5
G01 Y-4
G01 X-.5
G01 Y4
G01 X-.5
G01 Y-4
G4 P2
