// ============================================
// GMSH Geometry File: Quarter Annular Disc
// ============================================

// --------------------------------------------
// Parameters (modify these as needed)
// --------------------------------------------
r_0 = 1.0;      // Inner radius
r_f = 2.0;      // Outer radius

// Mesh parameters
mesh_inner = 0.04;   // Mesh size at inner radius (finer)
mesh_outer = 0.12;    // Mesh size at outer radius (coarser)

// --------------------------------------------
// Geometry Definition
// --------------------------------------------

// Center point
Point(1) = {0, 0, 0, mesh_inner};

// Inner arc points (quarter circle)
Point(2) = {r_0, 0, 0, mesh_inner};      // Inner radius at 0 degrees
Point(3) = {0, r_0, 0, mesh_inner};      // Inner radius at 90 degrees
Point(4) = {r_0/Sqrt(2), r_0/Sqrt(2), 0, mesh_inner};  // Inner radius at 45 degrees (for arc definition)

// Outer arc points (quarter circle)
Point(5) = {r_f, 0, 0, mesh_outer};      // Outer radius at 0 degrees
Point(6) = {0, r_f, 0, mesh_outer};      // Outer radius at 90 degrees
Point(7) = {r_f/Sqrt(2), r_f/Sqrt(2), 0, mesh_outer};  // Outer radius at 45 degrees (for arc definition)

// --------------------------------------------
// Lines and Arcs
// --------------------------------------------

// Inner arc (inlet) - using Circle arc with center point
Circle(1) = {2, 1, 4};   // Inner arc first half (0 to 45 degrees)
Circle(2) = {4, 1, 3};   // Inner arc second half (45 to 90 degrees)

// Outer arc (outlet) - using Circle arc with center point
Circle(3) = {5, 1, 7};   // Outer arc first half (0 to 45 degrees)
Circle(4) = {7, 1, 6};   // Outer arc second half (45 to 90 degrees)

// Radial lines connecting inner and outer arcs
Line(5) = {2, 5};        // Radial line at 0 degrees
Line(6) = {3, 6};        // Radial line at 90 degrees

// --------------------------------------------
// Curve Loops and Surface
// --------------------------------------------

// Define curve loop (counter-clockwise)
// Start at inner radius (0 deg), go along inner arc, then radial, then outer arc back, then radial
Curve Loop(1) = {1, 2, 6, -4, -3, -5};

// Create plane surface
Plane Surface(1) = {1};

// --------------------------------------------
// Mesh Control - Finer at inner radius
// --------------------------------------------

// Distance field from inner arc for graded mesh
Field[1] = Distance;
Field[1].CurvesList = {1, 2};
Field[1].Sampling = 100;

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = mesh_inner;
Field[2].SizeMax = mesh_outer;
Field[2].DistMin = 0;
Field[2].DistMax = r_f - r_0;

Background Field = 2;

// --------------------------------------------
// Mesh Settings
// --------------------------------------------

// Set mesh algorithm (6 = Frontal-Delaunay for triangles)
Mesh.Algorithm = 6;

// Force linear triangular elements (order 1)
Mesh.ElementOrder = 1;

// Ensure 2D mesh
Mesh.Smoothing = 5;

// --------------------------------------------
// Physical Groups (Entity Sets)
// --------------------------------------------

// Inlet: Inner arc curves
Physical Curve("inlet", 100) = {1, 2};

// Outlet: Outer arc curves  
Physical Curve("outlet", 200) = {3, 4};

// Radial boundaries (if needed)
Physical Curve("symmetry_x", 300) = {5};  // Line along x-axis
Physical Curve("symmetry_y", 400) = {6};  // Line along y-axis

// Domain: All surface elements
Physical Surface("domain", 500) = {1};

// --------------------------------------------
// Generate Mesh
// --------------------------------------------
Mesh 2;

// Optional: Save mesh (uncomment if needed)
// Save "quarter_annulus.msh";
