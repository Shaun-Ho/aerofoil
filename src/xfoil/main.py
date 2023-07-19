from xfoil.xfoil_wrapper import call_xfoil

if __name__ == "__main__":
    # user inputs
    aerofoil_name = "NACA0012"

    # viscoscity
    Re_start = 3e6
    Re_end = 3e6
    n_Re_intervals = 10

    # angle 
    angle_of_attack_start = -2
    angle_of_attack_end = 2
    angle_of_attack_interval = 0.5

    # turbulence setting
    x_transition_top = None
    x_transition_bot = None
    N_crit = 9

    # xfoil config
    n_iter_terminate = 50
   
    call_xfoil(
        aerofoil_name=aerofoil_name,
        Re_start=Re_start, 
        Re_end=Re_end,
        n_Re_intervals=n_Re_intervals,
        alpha_i=angle_of_attack_start,
        alpha_f=angle_of_attack_end,
        alpha_step=angle_of_attack_interval,
        x_transition_top=x_transition_top,
        x_transition_bot=x_transition_bot,
        n_iter_terminate=n_iter_terminate,
        N_crit=N_crit,
    )