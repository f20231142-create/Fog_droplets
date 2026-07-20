"""
Python translation of fog_og.m
Paired with the manuscript "Dynamics of fog droplets on a harp wire" by
Nicholas Kowalski and Jonathan Boreyko.

This program calculates position, velocity, and acceleration of a water
droplet sliding down a vertical wire, merging with other droplets along
the way. The model system considers a vertical wire with n droplets along
it, where each droplet is initially static. Each droplet is slowly growing
over time due to an incoming fog stream. Appreciable droplet sliding
initiates by the coalescence of a top pair of droplets; the merged droplet
subsequently coalesces with all underlying droplets as it moves down the
wire.

Translated as literally as possible from the original MATLAB code
(fog_og.m). Arrays that are 1-indexed in MATLAB (L, V, b, x, vel, a) are
kept 1-indexed here too, by padding index 0 with a dummy placeholder, so
that the numerical logic, indices, and variable names match the MATLAB
source exactly.
"""

import numpy as np
import matplotlib.pyplot as plt
import math


# ----------------------------------------------------------------------
# Helper: MATLAB-style cosd (cosine of an angle given in degrees)
# ----------------------------------------------------------------------
def cosd(deg):
    return math.cos(math.radians(deg))


# ----------------------------------------------------------------------
# Introduction text
# ----------------------------------------------------------------------
def print_intro():
    print('> The following program is paired with the manuscript "Dynamics of fog droplets on a harp wire" by')
    print(' Nicholas Kowalski and Jonathan Boreyko. The program will calculate position, velocity, and')
    print(' acceleration of a water droplet sliding down a vertical wire, merging with other droplets along')
    print(' the way. The model system considers a vertical wire with n droplets along it, where each droplet')
    print(' is initially static. Each droplet is slowly growing over time due to an incoming fog stream.')
    print(' Appreciable droplet sliding initiates by the coalescence of a top pair of droplets; the merged')
    print(' droplet subsequently coalesces with all underlying droplets as it moves down the wire.')
    print('> When altering the physical system, please refer to the "Variables" section of this program to')
    print(' make appropriate parameter changes.')
    print('> Refer to Figure 1 in the main manuscript for a visual representation of the system as needed.')
    print('---')


# ----------------------------------------------------------------------
# Inputs (mirrors the MATLAB "%% Inputs" section)
# ----------------------------------------------------------------------
def get_inputs():
    # --- z: perfect spheres? ---
    k = 1
    while k == 1:
        z = float(input('> Would you like to approximate all droplets as perfect spheres (1 for yes, 0 for no): '))
        if z == 1:
            k = 0
        elif z == 0:
            k = 0
        else:
            print(' Invalid input; must enter 1 or 0.')

    # --- NumD: number of droplets ---
    k = 1
    while k == 1:
        NumD = int(input('> Enter the number of droplets along the wire (including the intial coalescing pair): '))
        if NumD < 2:
            print(' Invalid input; number must be greater than or equal to two.')
        else:
            k = 0

    # --- DataI: import from file or manual entry ---
    k = 1
    while k == 1:
        DataI = float(input('> Import data from a spreadsheet, or enter manually (1 for former, 0 for latter): '))
        if DataI == 1:
            k = 0
        elif DataI == 0:
            k = 0
        else:
            print(' Invalid input; must enter 1 or 0.')

    L = [None] * (NumD + 1)   # 1-indexed: L[1..NumD]
    b = [None]                # 1-indexed: b[1..NumD-2] (extended below)

    if DataI == 1:
        print('> Ensure the file to read is named "data.txt" in the same file location as this program.')
        print(' Values should be arranged in a single column, starting with the "2r_(M,j)" values, directly')
        print(' followed by "b_z" values.')
        print(' Values should be in descending order from the top of the wire, in units of millimeters.')
        print(' For the measured length "2r_(M,j)" values of droplets, start with the initial coalescing pair.')
        print(' For spacing "b_z" values between pairs of droplets, start with the pair beneath the top')
        print(' initial coalescing droplet.')
        print(' Press Enter to continue.')

        k = 1
        while k == 1:
            flag = 0
            input('')
            Imp = np.loadtxt('data.txt')
            Imp = np.atleast_1d(Imp)
            DataL = 2 * NumD - 2

            if len(Imp) > DataL:
                flag = 2
            if len(Imp) < DataL:
                flag = 3

            if flag == 0:
                Lmm = [None] * (NumD + 1)
                for NumDC in range(1, NumD + 1):
                    Lmm[NumDC] = Imp[NumDC - 1]
                    if Imp[NumDC - 1] <= 0:
                        flag = 1
                L = [None] * (NumD + 1)
                for NumDC in range(1, NumD + 1):
                    L[NumDC] = Lmm[NumDC] / 1000

                bmm = [None] * (NumD - 2 + 1)
                for NumDC in range(1, NumD - 2 + 1):
                    bmm[NumDC] = Imp[(NumDC + NumD) - 1]
                    if Imp[(NumDC + NumD) - 1] <= 0:
                        flag = 1
                b = [None] * (NumD - 2 + 1)
                for NumDC in range(1, NumD - 2 + 1):
                    b[NumDC] = bmm[NumDC] / 1000

            if flag == 1:
                print('> Invalid input; one of the entered values is less than or equal to zero.')
                print(' To try again with new data: press Enter to continue.')
                print(' To change the inputted number of droplets along the wire: terminate the program')
                print(' and re-run.')
            elif flag == 2:
                print('> Invalid input; too many values in the imported data file.')
                print(f' Data file must have {DataL:3.0f} entries (from number of droplets inputted')
                print(' along the wire).')
                print(' To try again with new data: press Enter to continue.')
                print(' To change the inputted number of droplets along the wire: terminate the program')
                print(' and re-run.')
            elif flag == 3:
                print('> Invalid input; too few values in the imported data file.')
                print(f' Data file must have {DataL:3.0f} entries (from number of droplets inputted')
                print(' along the wire).')
                print(' To try again with new data: press Enter to continue.')
                print(' To change the inputted number of droplets along the wire: terminate the program')
                print(' and re-run.')
            else:
                k = 0

        It = 1 if (len(b) - 1) > 0 else 0

    else:
        NumDC = 1
        Lmm = [None] * (NumD + 1)
        print('> Enter the measured length "2r_(M,j)" of all droplets along the wire (including the intial')
        print(' coalescing pair).')
        print(' These will be entered in the order of descending the wire, starting with the top initial')
        print(' coalescing droplet (see Figure 1 in the main manuscript).')
        while NumDC <= NumD:
            print(f' Droplet #{NumDC:3.0f}.')
            k = 1
            while k == 1:
                Lmm[NumDC] = float(input(' Enter the measured length "2r_(M,j)" of the stated droplet (mm): '))
                if Lmm[NumDC] <= 0:
                    print(' Invalid input; measured length must be greater than zero.')
                else:
                    k = 0
            NumDC = NumDC + 1

        L = [None] * (NumD + 1)
        for i in range(1, NumD + 1):
            L[i] = Lmm[i] / 1000

        if NumD > 2:
            It = 1
            NumDC = 1
            bmm = [None] * (NumD - 2 + 1)
            print('> Enter the spacing "b_z" between all pairs of droplets (excluding the initial coalescing')
            print(' pair.')
            print(' These will be entered in the order of descending the wire, starting with the pair')
            print(' beneath the top initial coalescing droplet (see Figure 1 in the main manuscript).')
            while NumDC <= (NumD - 2):
                print(f' Droplet pair #{NumDC:3.0f}.')
                k = 1
                while k == 1:
                    bmm[NumDC] = float(input(' Enter the spacing between the stated pair (mm): '))
                    if bmm[NumDC] <= 0:
                        print(' Invalid input; spacing must be greater than zero.')
                    else:
                        k = 0
                NumDC = NumDC + 1
            b = [None] * (NumD - 2 + 1)
            for i in range(1, NumD - 2 + 1):
                b[i] = bmm[i] / 1000
        else:
            It = 0
            b = [None, 0]

    # --- tau_merge: characteristic coalescence time (Improvement 2) ---
    k = 1
    while k == 1:
        tau_merge = float(input('> Enter the characteristic coalescence time "tau_merge" (s): '))
        if tau_merge <= 0:
            print(' Invalid input; tau_merge must be greater than zero.')
        else:
            k = 0

    return z, NumD, L, b, It, tau_merge


# ----------------------------------------------------------------------
# Wire configuration selection
# ----------------------------------------------------------------------
def select_wire_configuration():
    print('Select experimental wire configuration')
    print()
    print('1. Stainless steel wire (radius = 0.127 mm)')
    print()
    print('2. Stainless steel wire (radius = 0.254 mm)')
    print()
    print('3. Teflon-coated stainless steel wire (radius = 0.127 mm)')
    print()

    k = 1
    while k == 1:
        option = input('Enter option (1-3): ')
        if option == '1':
            rwmm = 0.127
            theta_r = 43
            theta_a = 77
            S1 = 2.73
            S2 = 0.2103
            beta = 0.08
            wire_type = 'Stainless steel'
            k = 0
        elif option == '2':
            rwmm = 0.254
            theta_r = 50
            theta_a = 84
            S1 = 2.0
            S2 = 0.23
            beta = 0.05
            wire_type = 'Stainless steel'
            k = 0
        elif option == '3':
            rwmm = 0.127
            theta_r = 89
            theta_a = 122
            S1 = 0.5
            S2 = -0.09
            beta = 0.03
            wire_type = 'Teflon-coated stainless steel'
            k = 0
        else:
            print(' Invalid input; must enter 1, 2, or 3.')

    print()
    print('Selected configuration')
    print()
    print(f'Wire type : {wire_type}')
    print()
    print(f'Wire radius : {rwmm} mm')
    print()
    print(f'Receding contact angle : {theta_r}\u00b0')
    print()
    print(f'Advancing contact angle : {theta_a}\u00b0')
    print()
    print(f'S1 = {S1}')
    print()
    print(f'S2 = {S2}')
    print()
    print(f'Beta = {beta}')
    print('---')

    return rwmm, theta_r, theta_a, S1, S2, beta


# ----------------------------------------------------------------------
# q(y): aspect-ratio function (depends on z, S1, S2 -- set inside run_simulation)
# ----------------------------------------------------------------------
def make_q(z, S1, S2):
    if z == 0:
        return lambda y: S1 * (y ** S2)
    else:
        return lambda y: 1


# ----------------------------------------------------------------------
# Main simulation (mirrors "%% Variables" through "%% Acceleration loop")
# ----------------------------------------------------------------------
def run_simulation(z, NumD, L, b, It, tau_merge, rwmm, theta_r, theta_a, S1, S2, beta):
    # ---------------- Variables ----------------
    # rwmm, theta_r, theta_a, S1, S2, beta are supplied by the selected
    # experimental wire configuration (see select_wire_configuration()).
    t = 0.0001       # s; time step
    the_r = theta_r  # degrees; receding contact angle of a critical/sliding drop, measured experimentally
    the_a = theta_a  # degrees; advancing contact angle of a critical/sliding drop, measured experimentally

    rw = rwmm / 1000
    l = math.pi * rw
    gam = 0.073
    g = 9.81
    rhow = 1000
    mu = 0.0010016
    rhoa = 1.1225

    q = make_q(z, S1, S2)

    V = [None] * (NumD + 1)
    for k in range(1, NumD + 1):
        V[k] = (4 / 3) * math.pi * (q(L[k]) ** 2) * ((L[k] / 2) ** 3)

    # ---------------- Initial sliding velocity ----------------
    rt = L[1] / 2
    rb = L[2] / 2
    Vd = V[1] + V[2]

    if z == 0:
        rd1 = rt + (rb / 9)
        k = 1
        while k == 1:
            Vguess = (4 / 3) * math.pi * ((S1 * (2 * rd1) ** S2) ** 2) * (rd1 ** 3)
            if abs((Vd - Vguess) / Vd) < 0.001:
                k = 0
            elif (Vd - Vguess) > 0:
                rd1 = rd1 + 1e-7
            else:
                rd1 = rd1 - 1e-7
    else:
        rd1 = ((3 / 4) * (1 / math.pi) * Vd) ** (1 / 3)

    Ld1 = 2 * rd1
    rd2 = q(Ld1) * rd1
    ft = (2 * q(L[1]) ** 1.6) + (q(L[1]) ** 3.2)
    fb = (2 * q(L[2]) ** 1.6) + (q(L[2]) ** 3.2)
    ff = (2 * q(Ld1) ** 1.6) + (q(Ld1) ** 3.2)
    dS = 4 * math.pi * gam * (
        (((ft / 3) ** (5 / 8)) * rt ** 2)
        + (((fb / 3) ** (5 / 8)) * rb ** 2)
        - (((ff / 3) ** (5 / 8)) * rd1 ** 2)
    )
    veli = ((2 * beta * dS) / (rhow * Vd)) ** (1 / 2)

    # ---------------- Initializations for loop ----------------
    NumDC = 1
    CoM = (((L[1] / 2) + (L[2] / 2)) * (rhow * V[1])) / ((rhow * V[1]) + (rhow * V[2]))

    count = None
    if It == 1:
        count = b[NumDC] + CoM - (Ld1 / 2) - (L[3] / 2)

    dif = cosd(the_r) - cosd(the_a)

    NITER = 999
    vel = [0.0] * (NITER + 2)   # 1-indexed: vel[1..2000]
    x = [0.0] * (NITER + 2)     # 1-indexed: x[1..2000]
    a = [0.0] * (NITER + 1)     # 1-indexed: a[1..1999]

    vel[1] = veli
    x[1] = 0

    Aproj1 = math.pi * (rd2 ** 2)
    if q(Ld1) == 1:
        phi = 1
        phic = 1
        phil = 1
    else:
        req = ((3 * 4) * Vd * (1 / math.pi)) ** (1 / 3)
        SAeq = 4 * math.pi * (req ** 2)
        SAd = 4 * math.pi * (((2 * ((rd1 * rd2) ** 1.6)) + ((rd2 * rd2) ** 1.6)) / 3) ** (1 / 1.6)
        phi = SAeq / SAd
        Aeq = math.pi * (req ** 2)
        phic = Aeq / Aproj1
        Aproj2 = math.pi * rd1 * rd2
        phil = Aeq / ((0.5 * SAd) - Aproj2)

    Fpin = l * gam * dif

    # ---------------- New state for Improvement 2 (finite-duration coalescence) ----------------
    # merge_energy_remaining holds surface energy (beta*dS) that has been
    # released by a coalescence event but not yet converted into kinetic
    # energy; merge_time_remaining is the time left in the current
    # tau_merge decay window. Both start empty/zero prior to any collision.
    merge_energy_remaining = 0.0
    merge_time_remaining = 0.0

    # ---------------- Collision reporting state ----------------
    # Purely for display purposes; does not affect the numerical
    # simulation in any way.
    collision_count = 0

    # ---------------- Acceleration loop (numerical calculations) ----------------
    # This section implements two improvements over the original algorithm,
    # while leaving every governing equation, the drag coefficient model,
    # the force calculations, the shape-factor equations, the radius
    # iteration, and the collision ordering unchanged:
    #
    #   Improvement 1 (exact collision-time interpolation): instead of the
    #   original "if x[i+1] > count" overshoot check, the droplet's motion
    #   is interpolated exactly to the collision location (x = count), the
    #   merge is processed there with no overshoot, and the remaining
    #   fraction of the timestep is integrated using freshly recomputed
    #   merged-droplet forces/acceleration. This repeats within the same
    #   nominal timestep if a second (or further) collision occurs during
    #   the remaining time.
    #
    #   Improvement 2 (finite-duration coalescence): the surface energy
    #   released at a collision (beta*dS) is no longer converted into
    #   kinetic energy instantly. Instead it is deposited into the
    #   merge_energy_remaining reservoir with decay time tau_merge, and is
    #   released gradually into the droplet's kinetic energy once per
    #   nominal timestep, after the position/velocity update, never inside
    #   the collision routine itself.

    dt = t  # alias matching the timestep notation used for the improvements

    def compute_a(vel_local):
        """Force-based acceleration of the sliding droplet at the given
        velocity, using the CURRENT droplet geometry (rd1, rd2, Vd, phi,
        phic, phil, Fpin). Same governing equations/force model as before;
        only factored out so it can be re-evaluated exactly at collision
        points and immediately after every merge."""
        if vel_local == 0:
            return 0.0
        Re = (rhow * (2 * rd2) * vel_local) / mu
        Cd1 = (8 / Re) * (1 / math.sqrt(phil))
        Cd2 = (16 / Re) * (1 / math.sqrt(phi))
        Cd3 = (3 / math.sqrt(Re)) * (1 / (phi ** (3 / 4)))
        Cd4 = -math.log10(phi)
        Cd5 = -((-Cd4) ** 0.2)
        Cd6 = 0.42 * (10 ** (0.4 * Cd5)) * (1 / phic)
        Cd = Cd1 + Cd2 + Cd3 + Cd6

        alp = 4
        Fgrav = rhow * Vd * g
        Fda = 0.5 * Cd * rhoa * Aproj1 * (vel_local ** 2)
        Fvb = (2 * math.pi * rd1 * rw) * mu * (vel_local / (2 * rd2))
        Fvw = alp * gam * math.pi * rw * (((10 * mu * vel_local) / gam) ** (2 / 3))

        return (Fgrav - Fpin - Fda - Fvb - Fvw) / (rhow * Vd)

    def do_merge(v_collision):
        """Process an exact collision at the current 'count' location,
        using the same governing equations as the original collision block
        (conservation of momentum, then the surface-energy calculation).
        The only change from the original is that beta*dS is NOT added to
        the kinetic energy here; it is deposited into merge_energy_remaining
        for gradual release (Improvement 2). Returns the droplet velocity
        immediately after momentum conservation (i.e. before any gradual
        energy release)."""
        nonlocal NumDC, Vd, rd1, rd2, Ld1, phi, phic, phil, Aproj1, count, It
        nonlocal merge_energy_remaining, merge_time_remaining

        NumDC = NumDC + 1
        NumDL = NumDC + 1

        Ei = 0.5 * rhow * Vd * (v_collision ** 2)
        v_post_momentum = (Vd * v_collision) / (Vd + V[NumDL])
        Em = 0.5 * rhow * (Vd + V[NumDL]) * (v_post_momentum ** 2)
        dEm = Em - Ei  # kept for fidelity with the original derivation (Em = Ei + dEm)

        ri = rd1
        Li = Ld1
        Vi = Vd
        Vd = Vd + V[NumDL]

        if z == 0:
            rd1 = ri + ((L[NumDL] / 2) / 9)
            k = 1
            while k == 1:
                Vguess = (4 / 3) * math.pi * ((S1 * (2 * rd1) ** S2) ** 2) * (rd1 ** 3)
                if abs((Vd - Vguess) / Vd) < 0.001:
                    k = 0
                elif (Vd - Vguess) > 0:
                    rd1 = rd1 + 1e-7
                else:
                    rd1 = rd1 - 1e-7
        else:
            rd1 = ((3 / 4) * (1 / math.pi) * Vd) ** (1 / 3)

        Ld1 = 2 * rd1
        rd2 = q(Ld1) * rd1

        fd = (2 * q(Li) ** 1.6) + (q(Li) ** 3.2)
        fb = (2 * q(L[NumDL]) ** 1.6) + (q(L[NumDL]) ** 3.2)
        ff = (2 * q(Ld1) ** 1.6) + (q(Ld1) ** 3.2)

        dS = 4 * math.pi * gam * (
            (((fd / 3) ** (5 / 8)) * ri ** 2)
            + (((fb / 3) ** (5 / 8)) * (L[NumDL] / 2) ** 2)
            - (((ff / 3) ** (5 / 8)) * rd1 ** 2)
        )

        # Improvement 2: defer the surface-energy release (beta*dS) instead
        # of instantly adding it to the kinetic energy (no more
        # "Ef = Ei + dEm + beta*dS" here). v_post_momentum (equivalent to
        # sqrt(2*Em/(rhow*Vd))) already reflects Ei + dEm via conservation
        # of momentum above.
        merge_energy_remaining += beta * dS
        merge_time_remaining = tau_merge

        Aproj1 = 2 * math.pi * (((((rd1 * rd2) ** 1.6) + (2 * (rd2 ** 3.2))) / 3) ** (1 / 1.6))

        if q(Ld1) == 1:
            phi = 1
            phic = 1
            phil = 1
        else:
            req = ((3 * 4) * Vd * (1 / math.pi)) ** (1 / 3)
            SAeq = 4 * math.pi * (req ** 2)
            SAd = 4 * math.pi * (((2 * ((rd1 * rd2) ** 1.6)) + ((rd2 * rd2) ** 1.6)) / 3) ** (1 / 1.6)
            phi = SAeq / SAd
            Aeq = math.pi * (req ** 2)
            phic = Aeq / Aproj1
            Aproj2 = math.pi * rd1 * rd2
            phil = Aeq / ((0.5 * SAd) - Aproj2)

        if NumDC < (NumD - 1):
            CoM = (((Li / 2) + (L[NumDL] / 2)) * (rhow * Vi)) / ((rhow * Vi) + (rhow * V[NumDL]))
            xCoM = (count + ri + (L[NumDL] / 2)) - CoM
            count = xCoM + CoM + b[NumDC] - rd1 - L[NumDL + 1]
        else:
            It = 0

        return v_post_momentum

    for i in range(1, NITER + 1):
        vel_cur = vel[i]
        x_cur = x[i]
        a_last = 0.0
        t_left = dt

        while t_left > 0:
            if vel_cur == 0:
                # Same "stuck" handling as the original code: at zero
                # velocity, the velocity-dependent forces vanish (and Re
                # would otherwise divide by zero), so no force-based motion
                # occurs this sub-step.
                a_local = 0.0
                vel_candidate = 0.0
                x_candidate = x_cur
            else:
                a_local = compute_a(vel_cur)
                vel_candidate = vel_cur + a_local * t_left
                if vel_candidate <= 0:
                    vel_candidate = 0.0
                    x_candidate = x_cur
                else:
                    x_candidate = x_cur + vel_cur * t_left + 0.5 * a_local * (t_left ** 2)

            a_last = a_local

            if It == 1 and x_candidate > count:
                # ---- Improvement 1: exact collision-time interpolation ----
                denom = x_candidate - x_cur
                alpha = (count - x_cur) / denom if denom != 0 else 0.0
                alpha = max(0.0, min(alpha, 1.0))

                dt_collision = alpha * t_left
                dt_remaining = t_left - dt_collision

                x_cur = count  # advance only until x = count; no overshoot
                v_collision = vel_cur + a_local * dt_collision  # velocity at collision, using current acceleration

                # ---- Collision reporting (display only; does not affect the simulation) ----
                collision_count += 1
                collision_time = ((i - 1) * dt) + dt_collision
                collision_position_mm = x_cur * 1000
                print(f'Collision {collision_count}')
                print(f'Time     : {collision_time:.5f} s')
                print(f'Position : {collision_position_mm:.3f} mm')
                print()

                # Perform the collision exactly at this location (no
                # overshoot). Forces/acceleration for the merged droplet
                # are recomputed from scratch on the next sub-step via
                # compute_a(), using the freshly updated rd1, rd2, Vd,
                # phi, phic, phil (Step 5 of Improvement 1).
                vel_cur = do_merge(v_collision)

                # Integrate the merged droplet over the remaining time; if
                # another collision occurs within dt_remaining, the while
                # loop processes it too (multiple collisions per timestep).
                t_left = dt_remaining
            else:
                vel_cur = vel_candidate
                x_cur = x_candidate
                t_left = 0.0

        # ---- Improvement 2: gradual (finite-duration) energy release ----
        # Executed exactly once per nominal timestep, after the normal
        # position/velocity update above -- never inside do_merge().
        if merge_time_remaining > 0:
            dt_release = min(dt, merge_time_remaining)
            dE = merge_energy_remaining * dt_release / merge_time_remaining
            merge_energy_remaining -= dE
            merge_time_remaining -= dt_release

            Ecurrent = 0.5 * rhow * Vd * (vel_cur ** 2)
            Ecurrent += dE
            vel_cur = math.sqrt(2 * Ecurrent / (rhow * Vd))

        a[i] = a_last
        vel[i + 1] = vel_cur
        x[i + 1] = x_cur

    # Convert to mm, mm/s, mm/s^2 (drop the unused index-0 placeholder)
    x_mm = np.array(x[1:]) * 1000
    vel_mm = np.array(vel[1:]) * 1000
    a_mm = np.array(a[1:]) * 1000

    print('---')
    print('> Program completed.')
    print(f'> Time step used was {t:6.5f} seconds, beginning at t = 0 seconds.')
    print('See the returned arrays for position (x, mm), velocity (vel, mm/s), and acceleration')
    print('(a, mm/s^2) at each time step.')

    return x_mm, vel_mm, a_mm, t


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    print_intro()
    rwmm, theta_r, theta_a, S1, S2, beta = select_wire_configuration()
    z, NumD, L, b, It, tau_merge = get_inputs()
    x_mm, vel_mm, a_mm, t = run_simulation(
        z, NumD, L, b, It, tau_merge, rwmm, theta_r, theta_a, S1, S2, beta
    )

    # time vector: x and vel have one more element than a (initial state included)
    time_x = np.arange(len(x_mm)) * t
    time_a = np.arange(len(a_mm)) * t + t  # a(i) corresponds to interval starting at t=i*dt (1-indexed)

    fig, axs = plt.subplots(3, 1, figsize=(7, 10), sharex=True)

    axs[0].plot(time_x, x_mm, color='tab:blue')
    axs[0].set_ylabel('Position (mm)')
    axs[0].set_title('Sliding droplet position, velocity, and acceleration')

    axs[1].plot(time_x, vel_mm, color='tab:orange')
    axs[1].set_ylabel('Velocity (mm/s)')

    axs[2].plot(time_a, a_mm, color='tab:green')
    axs[2].set_ylabel('Acceleration (mm/s$^2$)')
    axs[2].set_xlabel('Time (s)')

    for ax in axs:
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/fog_harp_results.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
