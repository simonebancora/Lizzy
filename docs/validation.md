# Validation cases
We can identify some cases that have a reference solution (either analytical or established) and solve the same with Lizzy to compare results.

## Channel flow experiment
The channel flow experiment, as described in the well-known work by Weitzenbock, has an analytical solution. For a constant inlet pressure and a perfectly one-dimensional flow, the time of arrival of the flow front at a distance L from the inlet is expressed as:

$t = \frac{\phi \mu L^2}{2 \Delta p \mathbf{K}}$

### Case definition
To conduct the channel flow experiment, we will use the following values:
- $\phi$ = 0.5
- $\mu=0.1$ Pa$\cdot$s
- $\Delta p=$1.0E+05 Pa
- $\mathbf{K}$ = 1.0E-10 $\cdot I$ m$^2$

By plugging the values in Eq. (XXXX), and considering a distance L = 1m, we obtain a theoretical arrival time of: $t_{ref}$ = **2500s**. This shall be considered as the reference solution.

### Lizzy solution
We construct a rectangular mesh os dimensions L x W:
- L = 1 m
- W = 0.5 m

<div style="display: flex; justify-content: center;">
<img src="tutorials/images/validation_rect_mesh.png" alt="Alt text" width="450">
</div>

Assigning the values and running the simulation we obtain the following fill times as function of number of elements in the mesh:

<div style="display: flex; justify-content: center;">
<img src="tutorials/images/validation_rect_fill.png" alt="Alt text" width="450">
</div>


<div style="display: flex; justify-content: center;">
<img src="tutorials/images/validation_rect_err.png" alt="Alt text" width="450">
</div>

As the number of elements increases, the fill time of the part approaches the theoretical solution and the error decreases.

## Radial flow experiment
For this validation we will replicate the radial infusion experiment from

The analytical solution for time of arrival of the flow front at a radial distance $R$ from the center is: