# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.6
# ---

import numpy as np

# constants:
Cp = 1004.  # Specific heat of dry air at constant pressure [J/K*kg]
Cs = 1e+6  # Specific heat (Cs=3e+5 for 10 cm ground) [J/K*m2]
R = 287.05  # Gas constant dry air (J/(K*kg))
S0 = 1367.  # solar constant, Wm-2
sigma = 5.67e-8  # Stefan-Boltzmann constant [W/(m2*K4)]
In = 10.  # Long wave radiation at 51 km [W/m2]

# Set constants for SW bands:
# SW band names H2O:
SW_bands_H2O = ['H2O_1', 'H2O_2', 'H2O_3']
# SW band names O3:
SW_bands_O3 = ['O3_Hartley', 'O3_Huggins', 'O3_Chappuis']
# All SW band names:
SW_bands = SW_bands_H2O + SW_bands_O3
# LW band names:
LW_bands = ['H2O', 'O3', 'CO2']
# H2O: available energy for 3 bands water vapor (SW):
energy_bands_H2O = {'H2O_1': 0.73, 'H2O_2': 0.20, 'H2O_3': 0.07}
del_h2o = 0.346 * S0
# O3: available energy for 3 bands ozone (SW):
energy_bands_O3 = {'O3_Hartley': 0.002, 'O3_Huggins': 0.01, 'O3_Chappuis': .988}
del_o3 = 0.654 * S0


class Grid:
    def __init__(self, nr_boxes, dz=1000., scale_HSH=4000):
        """
        Initializes grid
        :param nr_boxes: Nr of boxes in vertical
        :param dz: Vertical thickness of boxes
        :param scale_HSH: scale height
        """
        self.nr_boxes = nr_boxes
        self.scale_HSH = scale_HSH
        self.dz = dz
        self.zi = dz * np.arange(nr_boxes + 1)
        self.z = (dz * np.arange(nr_boxes) + dz * np.arange(1, nr_boxes + 1)) / 2


class RadiationModel(Grid):

    def __init__(self, nr_boxes, atmos, r_gas, abs_conc, emis,
                 albedo, declinationAngle, latitude,
                 dz=1000., scale_HSH=4000, initial_temp=250., init_surface_temp=288.):
        """
        Initializes model
        :param nr_boxes: nr of boxes in vertical
        :param atmos: pandas dataframe containing standard temperature ('Temp') and pressure ('Pressure') of atm
        :param r_gas: pandas dataframe containing gas mixing ratios
        :param abs_conc: pandas dataframe containing absorption constants
        :param emis: pandas dataframe containing emissivity
        :param albedo: Albedo of surface
        :param declinationAngle: Declination angle
        :param latitude: Latitude of model
        :param dz: vertical thickness of boxes in column
        :param scale_HSH: Scale height
        :param initial_temp: Initial temperature
        :param init_surface_temp: Initial surface temperature
        """
        super().__init__(nr_boxes, dz=dz, scale_HSH=scale_HSH)
        self.albedo = albedo  # albedo of the surface
        self.declinationAngle = declinationAngle
        self.latitude = latitude
        self.atmos = atmos  # keeps temperature, pressure
        self.r_gas = r_gas  # keeps mass mixing ratios of gases H2O, CO2, O3
        self.emis = emis  # keeps emissivity/absorptivity for the gases
        self.abs_cons = abs_conc  # absorption constants for the absorption bands.
        self.density = atmos['Pressure'][0:-1] / (R * atmos['Temp'][0:-1]) * 100.  # Multiply pressure by 100 to get Pa
        self.initial_temp = initial_temp  # initial temperature atmosphere
        self.init_surface_temp = init_surface_temp  # initial temperature surface

    def compute_tau(self):  # Exercise 1
        """
        Computes optical thickness (tau) for each layer/box
        :return: Tau
        """
        # TODO EXERCISE 1
        tau = {}
        for band in SW_bands_H2O:
            tau[band] = 0.0 * np.zeros(self.nr_boxes)  # exercise 1
        for band in SW_bands_O3:
            tau[band] = 0.0 * np.zeros(self.nr_boxes)  # exercise 1
        return tau

    def runRadiationModel(self, n_t, dt, t0=0):
        """
        Runs the model
        :param n_t: Number of timesteps to run model
        :param dt: Timestep of model
        :param t0: Start time, default 0.
        :return: Dictionary of outputs
        """
        DeltaF_LW_down, DeltaF_LW_total, DeltaF_LW_up, DeltaF_SH, DeltaF_SW_down, LW_down, \
        LW_heating_rates, LW_up, SH_heating_rate, SW_down, SW_heating_rates, \
        T, heating_rates_total, mu, T_s = self.init_model_vars(n_t)

        # Initialize temperature and surface temperature
        T[:, 0] = T[:, 0] + self.initial_temp
        T_s[0] = self.init_surface_temp
        # Compute tau:
        tau = self.compute_tau()
        # Time loop:
        for i_t in np.arange(n_t - 1):
            if i_t % int(round(n_t / 10)) == 0:  # Print every 10th time
                print('%d of %d' % (i_t, n_t))
            # ***************SHORT WAVE RADIATION**********************
            # time:
            time = i_t * dt + t0
            # cosine to the zenith angle:
            mu[i_t] = np.sin(self.latitude) * np.sin(self.declinationAngle) + np.cos(self.latitude) * \
                      np.cos(self.declinationAngle) * np.cos(time * 2 * np.pi / 24.)

            if mu[i_t] > 0:  # senit angle >0: sun is up
                # H2O bands:
                for band in SW_bands_H2O:
                    S0_ = del_h2o * energy_bands_H2O[band]
                    SW_down[band][self.nr_boxes, i_t] = S0_ * mu[i_t]
                # O3 bands:
                for band in SW_bands_O3:
                    S0_ = del_o3 * energy_bands_O3[band]
                    SW_down[band][self.nr_boxes, i_t] = S0_ * mu[i_t]

            else:
                # If sun not up, all incoming SW set to zero:
                for band in SW_bands:
                    SW_down[band][self.nr_boxes, i_t] = 0.
            # Radiation downwards in each layer depends on radiation in the above layer and exponential
            # of optical thickness and zenith angle
            for band in SW_bands:
                for i_z in np.arange(self.nr_boxes)[::-1]:  # goes from top to bottom
                    # TODO EXERCISE 2
                    if mu[i_t] > 0:
                        SW_down[band][i_z, i_t] = 0.0  # Exercise 2
                    else:
                        SW_down[band][i_z, i_t] = 0.

                    # compute diff in incoming and outgoing radiation for each layer:
                    DeltaF_SW_down[band][i_z, i_t] = SW_down[band][i_z + 1, i_t] - SW_down[band][i_z, i_t]
            # Calculate heating rates SW:
            for band in SW_bands:
                # Heating rates SW [K/h]
                # TODO EXERCISE 3:
                SW_heating_rates[band][:, i_t] = 0.  # Exercise 3
                if band in SW_bands_H2O:
                    SW_heating_rates['H2O_tot'][:, i_t] = SW_heating_rates['H2O_tot'][:, i_t] + \
                                                          SW_heating_rates[band][:, i_t]  # TOTAL
                elif band in SW_bands_O3:
                    SW_heating_rates['O3_tot'][:, i_t] = SW_heating_rates['O3_tot'][:, i_t] + \
                                                         SW_heating_rates[band][:, i_t]  # TOTAL

            for band in SW_bands:
                SW_heating_rates['SW_tot'][:, i_t] = SW_heating_rates['SW_tot'][:, i_t] + \
                                                     SW_heating_rates[band][:, i_t]

            # ***********LONG WAVE RADIATION*****************
            # Long wave radiation upwards:
            # For the surface we assume that the earth is a black body and use Stefan Boltzmann's law:
            for band in LW_bands:
                LW_up[band][0, i_t] = sigma * (T_s[i_t]) ** 4
            for band in LW_bands:
                for i_z in np.arange(self.nr_boxes):
                    # TODO EXERCISE 4:
                    LW_up[band][i_z + 1, i_t] = 0.  # Exercise 4
                    DeltaF_LW_up[band][i_z, i_t] = LW_up[band][i_z, i_t] - LW_up[band][i_z + 1, i_t]

            # Long wave radiation downwards:
            for band in LW_bands:
                # Default incoming LW at top:
                LW_down[band][self.nr_boxes, i_t] = In
                for i_z in np.arange(self.nr_boxes)[::-1]:  # [::-1] gives reverse order
                    # TODO EXERCISE 5:
                    LW_down[band][i_z, i_t] = 0.  # Exercise 5

                # For surface temperature: Add all bands together
                LW_down['Surface'][i_t] = LW_down['Surface'][i_t] + LW_down[band][0, i_t]

                # Compute difference in incoming and outgoing radiation.
                # The radiation absorbed has effect on the heating rate of the layer
                for i_z in np.arange(self.nr_boxes):  #
                    DeltaF_LW_down[band][i_z, i_t] = LW_down[band][i_z + 1, i_t] - LW_down[band][i_z, i_t]

            # Compute total LW flux:
            for band in LW_bands:
                DeltaF_LW_total[band][:, i_t] = (DeltaF_LW_down[band][:, i_t] + DeltaF_LW_up[band][:, i_t])

            # Flux of SH from ground, omitting LH:
            if mu[i_t] > 0:
                SH0 = Cp * self.density[0] * 1.5e-1 * (T_s[i_t] - T[0, i_t])  # eq. 9.19a W&H
                # (CH=3E-3, U=5m/s)
            else:
                SH0 = 0

            # Energy flux given at surface by SH0 is distributed vertically:

            for i_z in np.arange(self.nr_boxes):
                DeltaF_SH[i_z, i_t] = SH0 * (
                        np.exp(-i_z * self.dz / self.scale_HSH) - np.exp(-(i_z + 1) * self.dz / self.scale_HSH))

            # Heating rate LW [K/h]
            # Hint: DeltaF_SH and DeltaF_LW_ total are both energy fluxes
            for band in LW_bands:
                # TODO EXERCISE 6:
                LW_heating_rates[band][:, i_t] = 0.0  # Exercise 6

                # Total heating rate LW:
                LW_heating_rates['LW_tot'][:, i_t] = LW_heating_rates['LW_tot'][:, i_t] + LW_heating_rates[band][:, i_t]

            # Heating rate SH
            SH_heating_rate[:, i_t] = 60 ** 2 * DeltaF_SH[:, i_t] / (self.dz * self.density * Cp)  # Exercise 6


        # Total heating rate LW & SW
            heating_rates_total[:, i_t] = LW_heating_rates['LW_tot'][:, i_t] + SW_heating_rates['SW_tot'][:, i_t]

            # Update surface temperature:
            SW_down_surf = 0
            for band in SW_bands:
                SW_down_surf += SW_down[band][0, i_t]
            # Update surface temperature:
            T_s[i_t + 1] = T_s[i_t] + ((1 - self.albedo) * SW_down_surf + LW_down['Surface'][i_t] - sigma * T_s[
                i_t] ** 4 - SH0) * 3600 / Cs
            # Update temperature:
            T[:, i_t + 1] = T[:, i_t] + (heating_rates_total[:, i_t] + SH_heating_rate[:, i_t]) * dt
        # Make dictionary of output:
        output = {'SW_down': SW_down, 'DeltaF_SW_down': DeltaF_SW_down, 'mu': mu, 'SW_heating_rates': SW_heating_rates,
                  'LW_up': LW_up, 'LW_down': LW_down, 'LW_heating_rates': LW_heating_rates, 'T': T, 'T_s': T_s,
                  'DeltaF_LW_total': DeltaF_LW_total, 'DeltaF_LW_down': DeltaF_LW_down, 'DeltaF_LW_up': DeltaF_LW_up,
                  'SH_heating_rate': SH_heating_rate, 'heating_rates_total': heating_rates_total}
        return output

    def init_model_vars(self, n_t):
        """
        Initializes variables to hold model output
        :param n_t: number of timesteps of model
        :return: declared variables to hold output
        """
        # Declaration of variables for run. Do not change!
        SW_down = {}
        LW_down = {}
        LW_up = {}
        # Fluxes are calculated at the interface between boxes and need to have nr_boxes+1 in length
        for band in SW_bands:
            SW_down[band] = np.zeros([self.nr_boxes + 1, n_t])
        for band in LW_bands:
            LW_down[band] = np.zeros([self.nr_boxes + 1, n_t])
            LW_up[band] = np.zeros([self.nr_boxes + 1, n_t])
        LW_down['Surface'] = np.zeros([n_t])
        SW_heating_rates = {}  # SW heating rates [K/h]
        LW_heating_rates = {}  # LW heating rates [K/h]
        DeltaF_SH = np.zeros([self.nr_boxes, n_t])  # difference in in and out sensible heat for each layer [w/m2]
        DeltaF_SW_down = {}  # difference in incoming and outgoing radiation for each layer [w/m2]
        DeltaF_LW_up = {}  # difference in incoming and outgoing radiation for each layer [w/m2]
        DeltaF_LW_down = {}  # difference in incoming and outgoing radiation for each layer [w/m2]
        DeltaF_LW_total = {}  # difference in incoming and outgoing radiation for each layer [w/m2]
        # Initialize for each band:
        for band in SW_bands:  # For each SW band
            SW_heating_rates[band] = np.zeros([self.nr_boxes, n_t])
            DeltaF_SW_down[band] = np.zeros([self.nr_boxes, n_t])
        for band in LW_bands:  # For each LW band
            LW_heating_rates[band] = np.zeros([self.nr_boxes, n_t])
            DeltaF_LW_up[band] = np.zeros([self.nr_boxes, n_t])
            DeltaF_LW_down[band] = np.zeros([self.nr_boxes, n_t])
            DeltaF_LW_total[band] = np.zeros([self.nr_boxes, n_t])

        SH_heating_rate = np.zeros([self.nr_boxes, n_t])  # [K/h]
        LW_heating_rates['LW_tot'] = np.zeros([self.nr_boxes, n_t])
        SW_heating_rates['H2O_tot'] = np.zeros([self.nr_boxes, n_t])
        SW_heating_rates['O3_tot'] = np.zeros([self.nr_boxes, n_t])
        SW_heating_rates['SW_tot'] = np.zeros([self.nr_boxes, n_t])
        heating_rates_total = np.zeros([self.nr_boxes, n_t])
        T = np.zeros([self.nr_boxes, n_t])  # Temperature
        mu = np.zeros(n_t)
        T_s = np.zeros(n_t)
        return DeltaF_LW_down, DeltaF_LW_total, DeltaF_LW_up, DeltaF_SH, DeltaF_SW_down, LW_down, \
               LW_heating_rates, LW_up, SH_heating_rate, SW_down, SW_heating_rates, \
               T, heating_rates_total, mu, T_s
