def prepare_data(data, target):
    """
    Adjusts data format
    :param data: list of list - each list contains binary values
    :param target: list contains binary values results
    :return: training data
    """

    training_data = []
    for index, item in enumerate(data):
        tmp_list = []
        for i in item:
            tmp_list.append(str(i))
        single_example = [tuple(tmp_list), target[index]]
        training_data.append(single_example)
    return training_data


def match(hypothesis, instance):
    """
    :param hypothesis: tuple
    :param instance: tuple
    :return: return True if hypothesis matches with instance, False otherwise
    """
    for idx, hyp in enumerate(hypothesis):
        ins_factor = instance[idx]
        if hyp != ins_factor:
            if hyp != '?' and ins_factor != '?':
                return False
    return True


def remove_not_matching(hypothesis, instance):
    """
    Remove hypothesis that not match
    :param hypothesis: equals to G - list of tuples
    :param instance: single record - tuple
    :return: hypothesis
    """
    copy_of_hypothesis = hypothesis[:]
    for g in hypothesis:
        if not match(g, instance):
            copy_of_hypothesis.remove(g)
    return copy_of_hypothesis[:]


def get_factor_contradictions(first_tuple, second_tuple):
    """
    :param first_tuple:
    :param second_tuple:
    :return: list of  contradictions (tuple)
    """
    contradictions = []
    for i, first_factor in enumerate(first_tuple):
        second_factor = second_tuple[i]
        if first_factor != second_factor:
            if first_factor != '?' and second_factor != '?':
                contradictions.append(i)

    return contradictions


def more_general(hyp1, hyp2):
    """
    :param hyp1: tuple
    :param hyp2: tuple
    :return: True or False
    """
    more_gen = False
    if match(hyp1, hyp2):
        more_gen = True
        for i, factor in enumerate(hyp2):
            if factor == '?' and hyp1[i] != '?':
                more_gen = False
    return more_gen


def more_specific(hyp1, hyp2):
    return more_general(hyp2, hyp1)


def get_min_generalization(s, sample):
    """
    :param s: instance of max specific - tuple
    :param sample: single record - tuple
    :return: tuple of max specific
    """
    contradictions = get_factor_contradictions(s, sample)
    specific_list = list(s)
    for contradiction in contradictions:
        if s[contradiction] == '*':
            specific_list[contradiction] = sample[contradiction]
        else:
            specific_list[contradiction] = '?'
    return tuple(specific_list)


def process_generalization(generalization, max_generic):
    """
    :param generalization:
    :param max_generic:
    :return: True or False
    """
    if not max_generic:
        return True
    for g in max_generic:
        if more_specific(generalization, g):
            return True
    return False


def remove_matching(hypotheses, instance):
    """
    Remove hypothesis that match
    :param hypotheses: list of tuple
    :param instance: tuple
    :return: hypotheses without matching records
    """
    copy_of_hypotheses = hypotheses[:]
    for s in hypotheses:
        if match(s, instance):
            copy_of_hypotheses.remove(s)
    return copy_of_hypotheses[:]


def get_min_specializations(g, instance):
    """
    Return min specializations
    :param g: tuple
    :param instance: tuple
    :return: list of tuple
    """
    specializations = []

    for i, factor in enumerate(g):
        if factor == '?':
            generic_list = list(g)
            if instance[i] == '0':
                generic_list[i] = '1'
            else:
                generic_list[i] = '0'
            specializations.append(tuple(generic_list))

    return specializations


def remove_more_specific(hypothesis):
    """
    :param hypothesis:
    :return:
    """
    copy_of_hypothesis = hypothesis[:]
    for first_g in hypothesis:
        for second_g in hypothesis:
            if first_g != second_g and more_specific(first_g, second_g):
                try:
                    copy_of_hypothesis.remove(first_g)
                    break
                except ValueError:
                    continue
    return copy_of_hypothesis[:]


class CalcCandidateElimination:
    """
    Candidate Elimination Class
    """

    def __init__(self, data, target):
        self.training_data = prepare_data(data, target)
        self.num_attributes = len(data[0])
        self.max_general = [tuple(['?' for i in range(self.num_attributes)])]   # G
        self.max_specific = [tuple(['*' for i in range(self.num_attributes)])]  # S
        self.numFactors = 4
        self.version_space = []

    def candidate_elimination(self):
        """
        G = list of tuple - [('?', '?', '?', '?')]
        S = list of tuple - [('*', '*', '*', '*')]
        training data = each record is a tuple with attributes values and 0 or 1 as results -
                        example: [ [('0', '0', '0', '0'), 1], [('0', '0', '0', '1'), 0] ]
        Execute candidate elimination algorithm
        :return: version space
        """

        for training_example in self.training_data:
            sample = training_example[0]
            result = training_example[1]

            # positive case
            if result == 1:
                # remove from G any hypothesis inconsistent
                self.max_general = remove_not_matching(self.max_general, sample)
                copy_of_max_specific = self.max_specific[:]
                for s in self.max_specific:
                    if not match(s, sample):
                        # remove s from S
                        copy_of_max_specific.remove(s)
                        generalization = get_min_generalization(s, sample)
                        # generalization
                        if process_generalization(generalization, self.max_general):
                            copy_of_max_specific.append(generalization)
                self.max_specific = copy_of_max_specific[:]

            # negative case
            elif result == 0:
                # remove from S any hypothesis inconsistent
                self.max_specific = remove_matching(self.max_specific, sample)
                new_max_generic = self.max_general[:]
                for g in self.max_general:
                    if match(g, sample):
                        # remove g from G
                        new_max_generic.remove(g)
                    specializations = get_min_specializations(g, sample)
                    # specializations
                    specializations = self.process_specializations(specializations, self.max_specific)
                    new_max_generic += specializations
                self.max_general = new_max_generic[:]

                self.max_general = remove_more_specific(self.max_general)

            # wrong branch
            else:
                # Should not happen
                print("Error! Wrong result")

        self.version_space = self.gen_version_space()
        return self.version_space

    def process_specializations(self, specializations, max_specific):
        """
        :param specializations: list of tuple
        :param max_specific: list of tuple
        :return: list of tuple
        """

        valid_specializations = []
        for s in max_specific:
            for hyp in specializations:
                if more_general(hyp, s):
                    valid_specializations.append(hyp)
                elif s == [tuple(['*' for factor in range(self.numFactors)])][0]:
                    valid_specializations.append(hyp)
        return valid_specializations

    def gen_version_space(self):
        """
        :return: version space - list
        """
        # add to version space all instances of G and S
        for i in self.max_general:
            self.version_space.append(i)
        for i in self.max_specific:
            self.version_space.append(i)

        for s in self.max_specific:
            for i in range(self.num_attributes):
                for g in self.max_general:
                    attributes = []
                    for j in range(self.num_attributes):
                        if j == i:
                            pass
                            attributes.append(s[i])
                        else:
                            pass
                            attributes.append(g[j])
                    self.version_space.append(tuple(attributes))

        return list(set(self.version_space))

    def prediction(self, new_data):
        """
        Predict final result for the new record
        :param new_data: list of list
        :return: 1 if is True or 0 otherwise
        """
        new_record = new_data[0]
        new_record_dict = dict(enumerate(new_record))
        classification_yes = 0
        classification_no = 0

        for instance in self.version_space:
            classification = False
            for index, attr in enumerate(instance):
                if attr != '?':
                    if str(new_record_dict[index]) == str(attr):
                        classification = True
                    else:
                        classification = False
                        break
            if classification:
                classification_yes += 1
            else:
                classification_no += 1

        if classification_yes > classification_no:
            return 1
        else:
            return 0
