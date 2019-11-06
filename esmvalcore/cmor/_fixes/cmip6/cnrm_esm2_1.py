"""Fixes for CNRM-ESM2-1."""
from ..fix import Fix
import cf_units

new_lats = [-78.31010985, -78.12948353, -77.94582993, -77.75905569,
            -77.56906686, -77.37576547, -77.17905289, -76.97882346,
            -76.7749755 , -76.56740085, -76.35598816, -76.14062679,
            -75.92120235, -75.69759868, -75.46970003, -75.23738747,
            -75.00054051, -74.74718467, -74.50211201, -74.25207444,
            -73.99695178, -73.73662761, -73.47098739, -73.19991796,
            -72.92330808, -72.6410544 , -72.353054  , -72.05921232,
            -71.75943931, -71.45365132, -71.14177225, -70.82373504,
            -70.49948169, -70.16895926, -69.83213178, -69.48896532,
            -69.13944282, -68.78355532, -68.42130258, -68.05269661,
            -67.67775775, -67.29650582, -66.90862274, -66.51325989,
            -66.11151886, -65.70331573, -65.28856659, -64.86719513,
            -64.43910217, -64.00422668, -63.56246948, -63.11375427,
            -62.65800095, -62.19512558, -61.72504807, -61.24769211,
            -60.76297379, -60.27082062, -59.77114868, -59.2638855 ,
            -58.74895477, -58.22628403, -57.69579697, -57.15742874,
            -56.61111069, -56.05677032, -55.49434662, -54.92377472,
            -54.34499359, -53.75794983, -53.1625824 , -52.55883789,
            -51.94667435, -51.32603455, -50.69688416, -50.0591774 ,
            -49.41287994, -48.75795746, -48.09438705, -47.42214203,
            -46.74119949, -46.051548  , -45.35317612, -44.6460762 ,
            -43.93025208, -43.20571136, -42.47245789, -41.73051071,
            -40.97989655, -40.22064209, -39.45278549, -38.67636108,
            -37.89142609, -37.09803009, -36.29623795, -35.48611832,
            -34.66775131, -33.84122086, -33.00661469, -32.16403961,
            -31.31359863, -30.4554081 , -29.58959389, -28.7162838 ,
            -27.83562279, -26.94775391, -26.05283546, -25.15103149,
            -24.24251175, -23.32746124, -22.40606308, -21.47851562,
            -20.54502296, -19.605793  , -18.66210938, -17.71509743,
            -16.76747131, -15.82362843, -14.88963032, -13.97249222,
            -13.07900047, -12.21489906, -11.3851366 , -10.59480476,
            -9.84941292,  -9.1537075 ,  -8.50995922,  -7.91714287,
            -7.3714118 ,  -6.86724281,  -6.39854765,  -5.95941591,
            -5.54450321,  -5.1491704 ,  -4.76948118,  -4.40214634,
            -4.04443884,  -3.69411659,  -3.3493495 ,  -3.00865722,
            -2.67085862,  -2.33502841,  -2.00046086,  -1.66663659,
            -1.33319354,  -0.99990022,  -0.66662848,  -0.33332792,
             0.        ,   0.33332792,   0.66662848,   0.99990022,
             1.33319354,   1.66663659,   2.00046086,   2.33502841,
             2.67085862,   3.00865722,   3.3493495 ,   3.69411659,
             4.04443884,   4.40214634,   4.76948118,   5.1491704 ,
             5.54450321,   5.95941591,   6.39854765,   6.86724281,
             7.3714118 ,   7.91714287,   8.50995922,   9.1537075 ,
             9.84941292,  10.59480476,  11.3851366 ,  12.21489906,
            13.07900047,  13.97249222,  14.88963032,  15.82362843,
            16.76747131,  17.71509743,  18.66210938,  19.605793  ,
            20.54499518,  21.4779822 ,  22.40397865,  23.32236149,
            24.23251133,  25.13383794,  26.0257901 ,  26.90785984,
            27.77958485,  28.64055043,  29.49038969,  30.32878485,
            31.15546609,  31.97021166,  32.77284639,  33.56324014,
            34.3413056 ,  35.1069964 ,  35.86030526,  36.60126   ,
            37.32992187,  38.04638267,  38.750761  ,  39.44320076,
            40.12386792,  40.79294734,  41.45064064,  42.09716415,
            42.73274625,  43.35762528,  43.97204697,  44.57626374,
            45.17053258,  45.75511325,  46.33026766,  46.89625695,
            47.45334275,  48.0017845 ,  48.54183939,  49.07376113,
            49.59779916,  50.11419933,  50.62320079,  51.12503869,
            51.61994169,  52.10813175,  52.58982474,  53.06522926,
            53.53454666,  53.99797104,  54.45568858,  54.90787732,
            55.35470726,  55.79633995,  56.23292769,  56.66461435,
            57.09153389,  57.51381116,  57.93155986,  58.34488469,
            58.75387887,  59.15862474,  59.55919177,  59.95563977,
            60.34801363,  60.73634652,  61.12065795,  61.50095275,
            61.87722169,  62.24944061,  62.6175688 ,  62.98155002,
            63.3413111 ,  63.6967619 ,  64.04779419,  64.39428222,
            64.73608175,  65.07303015,  65.40494546,  65.73162743,
            66.05285733,  66.36839722,  66.67799154,  66.98136628,
            67.27823129,  67.5682795 ,  67.85118942,  68.12662456,
            68.39423657,  68.65366673,  68.90454521,  69.14649675,
            69.37914038,  69.6020903 ,  69.81496214,  70.01737144,
            70.20893729,  70.38928469,  70.55804591,  70.71486276,
            70.85938872,  70.9912902 ,  71.11024871,  71.21595922,
            71.30812349,  71.38640637,  71.45032307,  71.49904241,
            71.53102143,  71.53102144]


class msftyz(Fix):
    """Fix msftyz."""

    def fix_metadata(self, cubes):
        """
        Fix standard and long name.

        Parameters
        ----------
        cube: iris.cube.CubeList

        Returns
        -------
        iris.cube.CubeList

        """
        for cube in cubes:
            gridlat = cube.coord('Ocean grid longitude mean')
            gridlat.var_name = 'rlat'
            gridlat.standard_name='grid_latitude'
            gridlat.units=cf_units.Unit('degrees')
            gridlat.long_name='Grid Latitude'
            gridlat.points = new_lats
            #print(gridlat.points)
            # These values are wrong - they are supposed to be latitude
            # values but they are actually y axis indices.

            basin = cube.coord('region')
            basin.var_name = 'basin'

            basin = cube.coord('Vertical W levels')
            basin.var_name = 'depth'
        return cubes
