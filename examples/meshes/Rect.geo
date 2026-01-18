SetFactory("OpenCASCADE");

// seed size:
s=0.025;

// add points:
Point(1) = {0, 0, 0, s};
Point(2) = {1, 0, 0, s};
Point(3) = {1, 0.5, 0, s};
Point(4) = {0, 0.5, 0, s};

// connect points by lines:
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};
Curve Loop(1) = {3, 4, 1, 2};

// create a surface (domain):
Plane Surface(1) = {1};

// assign physical groups - these will provide the labels to assign materials and boundary conditions:

// edges - we tag the left edge and name it "left_edge":
Physical Curve("left_edge", 5) = {4};

// edges - we tag the right edge and name it "right_edge":
Physical Curve("right_edge", 6) = {2};

// surfaces - we tag the entire domain and name it "domain":
Physical Surface("domain", 7) = {1};

// finally, we can use the "Transfinite" functionality to create a structured mesh and control the element size (optional) 
Transfinite Curve {3, 1} = 49 Using Progression 1;
Transfinite Curve {4, 2} = 25 Using Progression 1;
Transfinite Surface {1};

// the construction is complete, now we can call the Mesh command to create the mesh:
Mesh(2);
