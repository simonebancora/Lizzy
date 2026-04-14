// Gmsh project created on Sun Apr 12 19:29:36 2026
SetFactory("OpenCASCADE");

// Main rectangle: Lx x Ly
// Top-left racetrack: L1 x H

// Parameters
Lx = 1;      // Main rectangle length
Ly = 0.3;      // Main rectangle height
H = 0.002;     // Width of RT gap

// Mesh size
lc = 0.008;

// Define points
Point(1) = {0, 0, 0, lc};
Point(2) = {Lx, 0, 0, lc};
Point(3) = {Lx, Ly-H, 0, lc};
Point(4) = {0, Ly-H, 0, lc};
Point(5) = {Lx, Ly, 0, lc};
Point(6) = {0, Ly, 0, lc};

// Define lines
// Outer boundary
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};
Line(5) = {3, 5};
Line(6) = {4, 6};
Line(7) = {6, 5};


// Define curve loops
Curve Loop(1) = {1, 2, 3, 4};

Curve Loop(2) = {5, 3, 6, 7};

// Define plane surfaces
Plane Surface(1) = {1};
Plane Surface(2) = {2};

// Physical groups for boundaries
Physical Curve("left_edge") = {4, 6};
Physical Curve("right_edge") = {2, 5};

// Physical groups for surfaces (elemental)

Physical Surface("domain") = {1};
Physical Surface("racetrack") = {2};

//+
Transfinite Curve {1, 3, 7} = 150 Using Progression 1;
//+
Transfinite Curve {4, 2} = 30 Using Progression 1;
//+
Transfinite Curve {6, 5} = 3 Using Progression 1;
//+
Transfinite Surface {1};
//+
Transfinite Surface {2};

// the construction is complete, now we can call the Mesh command to create the mesh:
Mesh(2);