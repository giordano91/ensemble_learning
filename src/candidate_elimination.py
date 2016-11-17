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
    :param hypothesis: tuple - example ('?', '?', '?', '?', '?', '?')
    :param instance: tuple - example ('0', '0', '0', '0', '0', '0')
    :return: return True if hypothesis matches with instance, False otherwise

    examples:
    - ('0','?', '?') ('1','0', '0') False
    - ('?','?', '0'), ('1','0', '0') True
    - ('?','?', '?'), ('1','0', '0') True
    - ('1','0', '?'), ('?','0', '0') True
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
    :param hypothesis: equals to G - list of tuples - example [('?', '?', '?', '?', '?', '?')]
    :param instance: single record - tuple - example ('0', '0', '0', '0', '0', '0')
    :return: hypothesis
    """
    copy_of_hypothesis = hypothesis[:]
    for g in hypothesis:
        if not match(g, instance):
            copy_of_hypothesis.remove(g)
    return copy_of_hypothesis[:]


def get_factor_contradictions(first_tuple, second_tuple):
    """
    :param first_tuple: tuple - example ('*', '*', '*', '*', '*', '*')
    :param second_tuple: tuple - example ('0', '0', '0', '0', '0', '0')
    :return: list of contradictions

    Loop first_tuple and second_tuple and append the index of elements that are in contradiction
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
    :param hyp1: tuple - example ('?', '?', '?', '?', '?', '?')
    :param hyp2: tuple - example ('0', '0', '0', '0', '0', '0')
    :return: True or False

    examples:
    ('?', '?', '?'), ('Y', 'N', '?') True
    ('?', '?', '?'), ('Y', 'N', '?') True
    ('Y', 'N', '?'), ('Y', '?', '?') False
    ('Y', '?', '?'), ('?', 'N', '?') False

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
    :param s: instance of max specific - tuple - example ('*', '*', '*', '*', '*', '*')
    :param sample: single record - tuple - example ('0', '0', '0', '0', '0', '0')
    :return: tuple of max specific

    examples:
    - ('Y', 'N', 'Y'), ('N', 'N', 'Y') => ('?', 'N', 'Y')
    - ('0', '0', '0'), ('Y', 'N', 'Y') => ('Y', 'N', 'Y')
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
    :param generalization: tuple - example ('0', '0', '0', '0', '0', '0')
    :param max_generic: list of tuple - example [('?', '?', '?', '?', '?', '?')]
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
    :param g: tuple - example ('?', '?', '?', '?', '?', '?')
    :param instance: tuple - example ('1', '1', '1', '0', '0', '1')
    :return: list of tuple

    examples:
    - ('?', '?', '?') - ('1', '0', '1') => [('0', '?', '?'), ('?', '1', '?'), ('?', '?', '0')]
    - ('0', '?', '?') - ('0', '1', '0') => [('0', '0', '?'), ('0', '?', '1')]
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
        self.max_general = [tuple(['?' for i in range(self.num_attributes)])]   # G <- Maximally general hypotheses
        self.max_specific = [tuple(['*' for i in range(self.num_attributes)])]  # S <- Maximally specific hypotheses
        self.numFactors = 4
        self.version_space = []

    def candidate_elimination(self):
        """
        G = list of tuple - [('?', '?', '?', '?')]
        S = list of tuple - [('*', '*', '*', '*')]
        training data = each record is a list with two elements:
                        the first element is a tuple with attributes values and the second element is 0 or 1 as results.
                        example: [ [('0', '0', '0', '0'), 1], [('0', '0', '0', '1'), 0] ]

        Execute candidate elimination algorithm

        PseudoCode:

        for each training example d=<x,c(x)> do:
            if d is a positive example then do:
                remove from G any hypothesis that is inconsistent with d
                for each hypothesis s in S that is inconsistent with d do:
                    remove s from S
                    add to S all minimal generalizations h of s such that h consistent with d
                                                                            and some member of G is more general than h
                remove from S any hypothesis more general than another in S
            else (d is a negative example) do:
                remove from S any hypothesis that is inconsistent with d
                for each hypothesis g in G that inconsistent with d
                    remove g from G
                    add to G all minimal specializations h of g such that h consistent with d and
                                                                          some member of S is more specific than h
                    remove from G any hypothesis less general than another in G

        :return: version space
        """

        for training_example in self.training_data:
            sample = training_example[0]
            result = training_example[1]

            # positive example
            if result == 1:
                # remove from G any hypothesis that is inconsistent
                self.max_general = remove_not_matching(self.max_general, sample)
                copy_of_max_specific = self.max_specific[:]
                # for each hypothesis s in S
                for s in self.max_specific:
                    # that is inconsistent
                    if not match(s, sample):
                        # remove s from S
                        copy_of_max_specific.remove(s)
                        # add to S all minimal generalizations h of s such that h consistent with d
                        # and some member of G is more general than h
                        generalization = get_min_generalization(s, sample)
                        if process_generalization(generalization, self.max_general):
                            copy_of_max_specific.append(generalization)

                self.max_specific = copy_of_max_specific[:]

            # negative example
            elif result == 0:
                # remove from S any hypothesis that is inconsistent
                self.max_specific = remove_matching(self.max_specific, sample)
                new_max_generic = self.max_general[:]
                # for each hypothesis g in G
                for g in self.max_general:
                    # that is inconsistent
                    if match(g, sample):
                        # remove g from G
                        new_max_generic.remove(g)
                    # add to G all minimal specializations h of g such that h consistent with d
                    # and some member of S is more specific than h
                    specializations = get_min_specializations(g, sample)
                    specializations = self.process_specializations(specializations, self.max_specific)
                    new_max_generic += specializations

                self.max_general = new_max_generic[:]

                self.max_general = remove_more_specific(self.max_general)

            # wrong example
            else:
                # Should not happen
                print("Error! Wrong result")

        self.version_space = self.gen_version_space()
        return self.version_space

    def process_specializations(self, specializations, max_specific):
        """
        :param specializations: list of tuple - example [('0', '?', '?', '?', '?', '?')]
        :param max_specific: list of tuple - example [('0', '0', '?', '0', '0', '0')]
        :return: list of tuple

        examples:
        - [('?', '1', '0')] - [('1', '?', '0'), ('?', '1', '0'), ('?', '0', '0')] => [('?', '1', '0')]
        - [('1', '1', '0')] - [('0', '?', '?'), ('1', '?', '?'), ('?', '0', '?'), ('?', '?', '0'), ('?', '?', '1')]
            => [('1', '?', '?'), ('?', '?', '0')]
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
        For each tuple of S and for each tuple of G, add to 'attributes' list S's element if
        position indices are equal. Otherwise add G's element.
        :param: None
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
                            attributes.append(s[i])
                        else:
                            attributes.append(g[j])
                    self.version_space.append(tuple(attributes))

        # use 'set' to eliminate duplicate
        return list(set(self.version_space))

    def prediction(self, new_data):
        """
        Predict final result for the new record.
        For each version space tuple check if each attribute value (!= ?) is equal to the new value.
        :param new_data: list of list - user input - example [[0, 0, 0, 0, 0, 0]]
        :return: 1 if is True or 0 otherwise

        examples:
        <Sunny, Warm, ?, Strong, ?, ?> - <Sunny, Warm, Normal, Strong, Cool, Change> - classification_yes
        <Sunny, Warm, ?, Strong, ?, ?> - <Rainy, Cold, normal, Light, Warm, Same>    - classification_no

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
