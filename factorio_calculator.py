class FactorioCalculator:
    def __init__(self):
        self.foo = 1

    # TODO check if factorio gives total speed, or you have to - the prod speed loss, i think its total
    def get_crafting_time(self, base_time, craft_speed, speed_mod):
        """
        Return the time in second to craft a resource
        :param base_time: base time in seconds to craft the resource
        :param craft_speed: craft speed of the assembly/refinery/plant etc...
        :param speed_mod: Total speed % of the speed modules
        :return: time in seconds to craft a resource
        """
        return base_time / (craft_speed + (craft_speed * speed_mod/100))

    def get_output_pas(self, craft_time, prod_mod, output_yield):
        """
        Returns the resources crafted per assembly-seconds (pas)
        :param craft_time: craft time in seconds
        :param prod_mod: Total prod % of the prod modules
        :param output_yield: Output yield of crafting the resource
        :return: number of resources crafted pas, ie per assembly per second
        """
        return (output_yield + (output_yield * prod_mod / 100)) / craft_time

    def get_input_pas(self, craft_time, intput_yield):
        """
        Returns the input resources need per assembly-seconds (pas)
        :param craft_time: craft time in seconds
        :param output_yield: input yield needed to craft the resource
        :return: number resources need pas
        """
        return intput_yield / craft_time

    def get_assembly_requirements(self, wanted_yield, pas):
        """
        Returns the number of assemblies needed to provide the wanted yield
        :param wanted_yield: Wanted yield of the resource per second
        :param pas: per assembly-seconds of the resource
        :return: number of assemblies needed
        """
        return wanted_yield / pas

    def get_input_per_sec_requirements(self, assembly_num, pas):
        """
        Return the number of resources needed per seconds to provide the num of assemblies
        :param assembly_num: Number of assembly used
        :param pas: pas of the input
        :return: resource per seconds
        """
        return pas * assembly_num
