from dataclasses import dataclass

@dataclass(slots=True)
class TimeStep:
    index : int
    time : float
    dt : float
    P : any
    V : any
    V_nodal : any
    fill_factor : any
    flow_front : any
    write_out : bool
