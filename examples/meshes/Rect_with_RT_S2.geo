// Gmsh geometry file: Rectangle with RT regions at corners
// Main rectangle: Lx x Ly
// Top-left rectangle (RT_top): L1 x H
// Bottom-right rectangle (RT_bottom): L2 x H

// Parameters
Lx = 0.6;      // Main rectangle length
Ly = 0.3;      // Main rectangle height
H = 0.001;     // Height of RT regions
L1 = 0.3;     // Length of top-left RT region
L2 = 0.3;     // Length of bottom-right RT region

// Mesh size
lc = 0.01;

// Define points
// Main rectangle corners and RT region corners
Point(1) = {0, 0, 0, lc};              
Point(2) = {Lx - L2, 0, 0, lc};       
Point(3) = {Lx, 0, 0, lc};            
Point(4) = {Lx, H, 0, lc};            
Point(5) = {Lx, Ly, 0, lc};            
Point(6) = {L1, Ly, 0, lc};         
Point(7) = {0, Ly, 0, lc};            
Point(8) = {0, Ly - H, 0, lc};        
Point(9) = {L1, Ly - H, 0, lc};       
Point(10) = {Lx - L2, H, 0, lc};      

// Define lines
// Outer boundary lines
Line(1) = {1, 2};      
Line(2) = {2, 3};      
Line(3) = {3, 4};      
Line(4) = {4, 5};      
Line(5) = {5, 6};      
Line(6) = {6, 7};      
Line(7) = {7, 8};      
Line(8) = {8, 1};     

// Internal lines
Line(9) = {2, 10};     
Line(10) = {10, 4};    
Line(11) = {8, 9};     
Line(12) = {9, 6};    

// Define curve loops
// RT_top region: P8 -> P9 -> P6 -> P7 -> P8
Curve Loop(1) = {11, 12, 6, 7};

// RT_bottom region: P2 -> P3 -> P4 -> P10 -> P2
Curve Loop(2) = {2, 3, -10, -9};

// Domain (main region): P1 -> P2 -> P10 -> P4 -> P5 -> P6 -> P9 -> P8 -> P1
Curve Loop(3) = {1, 9, 10, 4, 5, -12, -11, 8};

// Define plane surfaces
Plane Surface(1) = {1};  // RT_top
Plane Surface(2) = {2};  // RT_bottom
Plane Surface(3) = {3};  // Domain

// Physical groups for boundaries
Physical Curve("inlet_zone") = {7, 8};    // Left edge (entire)
Physical Curve("outlet_zone") = {3, 4};   // Right edge (entire)

// Physical groups for surfaces (elemental)
Physical Surface("RT_top") = {1};
Physical Surface("RT_bottom") = {2};
Physical Surface("domain") = {3};

// Mesh settings
Mesh.Algorithm = 6;  // Frontal-Delaunay for 2D meshes
Mesh 2;
