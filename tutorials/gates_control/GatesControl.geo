// Gmsh project created on Sat Apr 18 15:53:43 2026
SetFactory("OpenCASCADE");
//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {0.35, 0, 0, 1.0};
//+
Point(3) = {0.7, 0, 0, 1.0};
//+
Point(4) = {1, 0, 0, 1.0};
//+
Point(5) = {1, 0.5, 0, 1.0};
//+
Point(6) = {0.7, 0.5, 0, 1.0};
//+
Point(7) = {0.35, 0.5, 0, 1.0};
//+
Point(8) = {0, 0.5, 0, 1.0};
//+
Line(1) = {1, 2};
//+
Line(2) = {2, 3};
//+
Line(3) = {3, 4};
//+
Line(4) = {4, 5};
//+
Line(5) = {5, 6};
//+
Line(6) = {6, 7};
//+
Line(7) = {7, 8};
//+
Line(8) = {8, 1};
//+
Line(9) = {2, 7};
//+
Line(10) = {3, 6};
//+
Curve Loop(1) = {7, 8, 1, 9};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {6, -9, 2, 10};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {5, -10, 3, 4};
//+
Plane Surface(3) = {3};
//+
Transfinite Curve {8, 9, 10, 4} = 30 Using Progression 1;
//+
Transfinite Curve {1, 7, 6, 2} = 35 Using Progression 1;
//+
Transfinite Curve {3, 5} = 30 Using Progression 1;
//+
Transfinite Surface {1};
//+
Transfinite Surface {2};
//+
Transfinite Surface {3};
//+
Extrude {0, 0, 0.01} {
  Curve{8}; Layers {1}; 
}
//+
Extrude {0, 0, 0.01} {
  Curve{9}; Layers {1}; 
}
//+
Extrude {0, 0, 0.01} {
  Curve{10}; Layers {1}; 
}
//+
Physical Curve("edge_1", 20) = {13};
//+
Physical Curve("edge_2", 21) = {16};
//+
Physical Curve("edge_3", 22) = {19};
//+
Physical Surface("inlet", 23) = {4, 5, 6};
//+
Physical Surface("domain", 24) = {1, 2, 3};
